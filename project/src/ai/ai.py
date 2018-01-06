import importlib
import numpy as np

import src.ai.board_info as board_info
import src.utils.file_io as io
import src.ai.heuristics as heur
import src.ai.bot_learning as bot_learn

PLUGIN_PATH = 'src.ai.bots'  # this is lazy but writing it dynamically is too much of a pain right now.
TRAIN_INTERVAL = 50
TRAINING_MAP_RATE = 0.8


class AI:

    def __init__(self, game_state):
        self.bot = None
        self.opponent_profile = None
        self.opponent_name = game_state['OpponentId']
        self.game_id = game_state['GameId']
        self.heuristic_info = None
        self.bot_location = None
        if board_info.is_there_land(np.array(game_state['MyBoard'])):
            self.map_type = 'land'
        else:
            self.map_type = 'no-land'

    # Receive the name of a bot module to load from the 'bots' sub-folder.
    # Class name needs to be "Bot" to be found.
    def load_bot(self, name, heuristic_choices=None):
        self.opponent_profile = io.load_profile(name, self.opponent_name)
        self.display_play_stats()

        self.bot_location = PLUGIN_PATH + '.' + name
        # Gets the class Bot and creates an instance of it.
        self.bot = getattr(importlib.import_module(self.bot_location), 'Bot')()

        if not self.opponent_profile:
            self._generate_profile()

        if heuristic_choices:
            self._load_heuristics(heuristic_choices)

    # Asks bot to either place its ships or start hunting based on game state.
    def make_decision(self, game_state):
        if game_state['Round'] == 0:
            return self.bot.place_ships(game_state)
        else:
            return self.bot.make_move(game_state)

    # Load the selected heuristics of a bot.
    def _load_heuristics(self, heuristic_names):
        set_heuristics = getattr(self.bot, "set_heuristics", None)
        # Check if the bot has a heuristics setting function.
        if callable(set_heuristics):
            heuristics = []
            self.heuristic_info = []
            # For each heuristic, load the respective function and weight.
            for name in heuristic_names:

                # Check if a there already is a heuristic value for this name.
                if name not in self.opponent_profile['heuristics']:
                    continue

                heuristic_func = getattr(heur, name)
                # Try to load the heuristic relevant to the map type.
                if self.map_type in self.opponent_profile['heuristics'][name]:
                    heuristic_val = self.opponent_profile['heuristics'][name][self.map_type]
                    heur_type = self.map_type
                # Load a generic heuristic
                else:
                    heuristic_val = self.opponent_profile['heuristics'][name]['generic']
                    heur_type = 'generic'

                self.heuristic_info.append((name, heuristic_val))
                print('Loading a', heur_type, 'heuristic:', '\'' + name + '\'', 'of value', heuristic_val)
                heuristics.append((heuristic_func, heuristic_val))
            # Set the heuristics for the bot.
            set_heuristics(heuristics)

    def finish_game(self, train_bot=False):
        # If we allow training, there is enough game and we are at a training interval.
        if train_bot and \
                len(self.opponent_profile['games']) % TRAIN_INTERVAL == 0 \
                and len(self.opponent_profile['games']) >= bot_learn.GAME_COUNT:
            self._train_bot()

    def _train_bot(self):

        o = bot_learn.Optimiser(self.bot.bot_name, self.opponent_name, self.bot_location)
        o.prepare_heuristics([h[0] for h in self.heuristic_info])
        o.set_optimisation_type('minimise')
        map_type, games = self._select_training_type()
        o.prepare_offensive_games(games)
        result = o.optimise()
        self._save_heuristics(result[:-1], map_type)

    # Based on the distribution of land and no-land games in the training data, choose a specific weighted variant.
    def _select_training_type(self):

        game_dict = self.opponent_profile['games']
        games = [g for g in sorted(game_dict, reverse=True)[:bot_learn.GAME_COUNT]]

        for h in self.heuristic_info:
            name = h[0]
            # If any heuristic does not have a generic weighting yet.
            if name not in self.opponent_profile['heuristics'] or \
                    'generic' not in self.opponent_profile['heuristics'][name]:
                return 'generic', games

        no_land_games = []
        land_games = []

        for g in games:
            if game_dict[g]['map_type'] == 'land':
                land_games.append(g)
            else:
                no_land_games.append(g)

        # If there are not enough land or no-land maps to dominate at least the map rate, still choose generic.
        if float(max(len(land_games), len(no_land_games))) / bot_learn.GAME_COUNT < TRAINING_MAP_RATE:
            return 'generic', games

        if len(land_games) > len(no_land_games):
            return 'land', land_games
        else:
            return 'no-land', no_land_games

    def _save_heuristics(self, values, map_type):
        for h, val in zip(self.heuristic_info, values):
            name = h[0]
            if name not in self.opponent_profile['heuristics']:
                self.opponent_profile['heuristics'][name] = {}

            if map_type in self.opponent_profile['heuristics'][name]:
                print('Replacing', map_type, 'heuristic', '\'' + name + '\'', 'of value',
                      self.opponent_profile['heuristics'][name][map_type], 'with:', val)
            else:
                print('Setting', map_type, 'heuristic', '\'' + name + '\'', 'with:', val)
            self.opponent_profile['heuristics'][name][map_type] = val

        io.save_profile(self.opponent_profile, self.bot.bot_name, self.opponent_name)

    # Add the current game (has to have ended) to the bot's opponent profile.
    def add_game_to_profile(self, game_state, won):

        performance = self._assess_game_performance(game_state)
        self.opponent_profile['games'][self.game_id] = performance['games']

        # Ascertain if the game was actually won or not.
        self.opponent_profile['games'][self.game_id].update({'victory': won})

        # Tag game as either land or no land for later analysis.
        self.opponent_profile['games'][self.game_id].update({'map_type': self.map_type})

        # Add list of heuristics and values used to game.
        if hasattr(self.bot, "set_heuristics"):
            self.opponent_profile['games'][self.game_id].update({'heuristics': self.heuristic_info})

        io.save_profile(self.opponent_profile, self.bot.bot_name, self.opponent_name)

    # Measure how well a game went.
    def _assess_game_performance(self, final_state):
        performance = {}

        # If the bot has any performance metrics, get those.
        get_bot_performance = getattr(self.bot, 'get_performance_metrics', None)
        if callable(get_bot_performance):
            performance = get_bot_performance(final_state)

        # Additionally, get general accuracy/evasion metrics.
        bot_stats = board_info.count_hits_and_misses(final_state['MyBoard'])
        opp_stats = board_info.count_hits_and_misses(final_state['OppBoard'])

        accuracy = opp_stats['hits'] / (opp_stats['hits'] + opp_stats['misses'])
        evasion = 1 - bot_stats['hits'] / (opp_stats['hits'] + opp_stats['misses'])

        metrics = {'accuracy': accuracy, 'evasion': evasion}
        if 'games' in performance:
            performance['games'].update(metrics)
        else:
            performance.update({'games': metrics})

        return performance

    # Generates an empty opponent profile.
    def _generate_profile(self):
        self.opponent_profile = {'bot_name': self.bot.bot_name,
                                 'opponent_name': self.opponent_name,
                                 # Contains mapping of game_id:[interesting statistics about the game]
                                 'games': {},
                                 # Contains current heuristic values to use for the opponent.
                                 'heuristics': {},
                                 # Anything else.
                                 'misc': {}}

    # Computes and displays play-time stats in this match-up.
    def display_play_stats(self):
        if self.opponent_profile:
            print('\n---', self.opponent_profile['bot_name'], 'vs:', self.opponent_profile['opponent_name'], '---')

            game_stats = self.opponent_profile['games'].values()
            print('Games played:', len(game_stats))

            wins = [game['victory'] for game in game_stats]
            avg_wins = wins.count(True) / len(wins)
            win_str = 'Win rate: '+ '{:.3f}'.format(avg_wins * 100) + '%'

            map_wins = [game['victory'] for game in game_stats if game['map_type'] == self.map_type]
            if map_wins:
                avg_map_wins = map_wins.count(True)/len(map_wins)
                win_str += '     '+self.map_type+': '+'{:.3f}'.format(avg_map_wins * 100) + '%'

            print(win_str)

            avg_accuracy = np.average([game['accuracy'] for game in game_stats])
            avg_evasion = np.average([game['evasion'] for game in game_stats])
            print('Average accuracy:', '{:.3f}'.format(avg_accuracy * 100) + '%     ',
                  'Average evasion:', '{:.3f}'.format(avg_evasion * 100) + '%')

            avg_map_accuracies = [g['accuracy'] for g in game_stats if g['map_type'] == self.map_type]
            avg_map_evasions = [g['evasion'] for g in game_stats if g['map_type'] == self.map_type]

            # In case this is the first game on this kind of map, do not show any performances.
            if avg_map_accuracies and avg_map_evasions:
                avg_map_accuracy = np.average(avg_map_accuracies)
                avg_map_evasion = np.average(avg_map_evasions)
                print('Average', self.map_type, 'accuracy:', '{:.3f}'.format(avg_map_accuracy * 100) + '%     ',
                      'Average', self.map_type, 'evasion:', '{:.3f}'.format(avg_map_evasion * 100) + '%')
            print()
