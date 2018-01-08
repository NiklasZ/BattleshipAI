import importlib
import numpy as np

import src.ai.board_info as board_info
import src.utils.file_io as io
import src.ai.heuristics as heur
import src.ai.bot_learning as bot_learn
import src.utils.game_recorder as gc

PLUGIN_PATH = 'src.ai.bots'  # this is lazy but writing it dynamically is too much of a pain right now.
TRAIN_INTERVAL = 50  # Consider training after this many games have been played against an opponent.
GAME_COUNT = 20  # Default number of games to train.
MAX_GAMES_WITHOUT_TRAINING = 200  # Force a training session after this many games have elapsed against the opponent.
UNDERPERFOMANCE_THRESHOLD = 0.1  # By how much a trained bot has to underperform to be retrained at a training interval.


class AI:

    def __init__(self, game_state):
        self.bot = None
        self.opponent_profile = None
        self.opponent_name = game_state['OpponentId']
        self.game_id = game_state['GameId']
        self.heuristic_info = None
        self.heuristic_choices = None
        self.bot_location = None
        if board_info.is_there_land(np.array(game_state['MyBoard'])):
            self.map_type = 'land'
        else:
            self.map_type = 'no-land'

    # Receive the name of a bot module to load from the 'bots' sub-folder.
    # Class name needs to be "Bot" to be found.
    def load_bot(self, name, heuristic_choices=None):
        self.opponent_profile = io.load_profile(name, self.opponent_name)
        self.heuristic_choices = heuristic_choices
        self.display_play_stats()

        self.bot_location = PLUGIN_PATH + '.' + name
        # Gets the class Bot and creates an instance of it.
        self.bot = getattr(importlib.import_module(self.bot_location), 'Bot')()

        if not self.opponent_profile:
            self._generate_profile()

        if heuristic_choices:
            if self._bot_has_heuristics():
                self._load_heuristics(heuristic_choices)
            else:
                print('Bot', self.bot.bot_name, 'does not use heuristics and is not trainable.')

    # Asks bot to either place its ships or start hunting based on game state.
    def make_decision(self, game_state):
        if game_state['Round'] == 0:
            return self.bot.place_ships(game_state)
        else:
            return self.bot.make_move(game_state)

    def finish_game(self, game_state, won, train_bot=False):

        self._add_game_to_profile(game_state, won)
        io.save_profile(self.opponent_profile, self.bot.bot_name, self.opponent_name)

        if train_bot and self._bot_has_heuristics() and self._decide_whether_to_train():
            self._train_bot()
        io.save_profile(self.opponent_profile, self.bot.bot_name, self.opponent_name)

    # Check if a bot has a possibility to set heuristics.
    def _bot_has_heuristics(self):
        set_heuristics = getattr(self.bot, "set_heuristics", None)
        return callable(set_heuristics)

    # Load the selected heuristics of a bot.
    def _load_heuristics(self, heuristic_names):

        set_heuristics = getattr(self.bot, "set_heuristics", None)
        heuristics = []
        self.heuristic_info = []
        # For each heuristic, load the respective function and weight.
        for name in heuristic_names:

            # Check if a this heuristic has ever been set.
            if name not in self.opponent_profile['heuristics']:
                print('Bot', self.bot.bot_name, 'has not trained', name, 'yet.')
                continue

            heuristic_func = getattr(heur, name)
            # Try to load the heuristic relevant to the map type.
            if self.map_type in self.opponent_profile['heuristics'][name]:
                heuristic_val = self.opponent_profile['heuristics'][name][self.map_type]
                heur_type = self.map_type

                self.heuristic_info.append((name, heuristic_val))
                print('Loading a', heur_type, 'heuristic:', '\'' + name + '\'', 'of value', heuristic_val)
                heuristics.append((heuristic_func, heuristic_val))
                # Set the heuristics for the bot.

            else:
                print('Bot', self.bot.bot_name, 'has not trained', name, 'for', self.map_type, 'maps yet.')

        set_heuristics(heuristics)

    def _decide_whether_to_train(self):
        # If we are not at a training interval:
        remainder = len(self.opponent_profile['games']) % TRAIN_INTERVAL
        if remainder != 0:
            print('No training as the training interval has not been reached. Will attempt after',
                  TRAIN_INTERVAL - remainder, 'game(s).')
            return False

        # If there are not enough games to train yet for a map type.
        map_type_count = len(self._select_training_games())
        if map_type_count < GAME_COUNT:
            print('No training as there are not enough games of type', self.map_type + '. Have: ' +
                  str(map_type_count) + '. Require:', GAME_COUNT)
            return False

        # If we have never trained a heuristic
        trained_heuristics = set(self.opponent_profile['heuristics'].keys())
        chosen_heuristics = set(self.heuristic_choices)
        if trained_heuristics != chosen_heuristics:
            print('Will commence training as', self.bot.bot_name, 'has not trained all chosen heuristics.')
            return True

        # If a heuristic has never been trained with a map
        for heuristic in self.opponent_profile['heuristics']:
            if self.map_type not in self.opponent_profile['heuristics'][heuristic]:
                print('Will commence training as', self.bot.bot_name, 'has not trained', heuristic, 'on a',
                      self.map_type, 'map.')
                return True

        # If we have not trained for MAX_GAMES_WITHOUT_TRAINING.
        if self.opponent_profile['misc']['games_since_training'][self.map_type] >= MAX_GAMES_WITHOUT_TRAINING:
            print('Will commence training as', self.bot.bot_name, 'has not been trained on', self.map_type, 'in',
                  self.opponent_profile['misc']['games_since_training'][self.map_type], 'games.')
            return True

        # If the current accuracy has sufficiently underperformed vs the
        accuracy_after_training = self.opponent_profile['misc']['accuracy_after_training'][self.map_type]
        accuracy_before_training = self.opponent_profile['misc']['accuracy_before_training'][self.map_type]
        if accuracy_after_training < accuracy_before_training * (1 - UNDERPERFOMANCE_THRESHOLD):
            print('Will commence training as', self.bot.bot_name + '\'s accuracy has dropped from:',
                  '{:.3f}'.format(accuracy_before_training * 100) + '%', 'to:',
                  '{:.3f}'.format(accuracy_after_training * 100) + '%')
            return True
        else:
            print('Skipping training as current accuracy of:',
                  '{:.3f}'.format(accuracy_after_training * 100) + '%', ' is still good enough vs. ',
                  '{:.3f}'.format(accuracy_before_training * 100) + '%')

        return False

    def _train_bot(self):

        o = bot_learn.Optimiser(self.bot.bot_name, self.opponent_name, self.bot_location)
        o.prepare_heuristics(self.heuristic_choices)
        o.set_optimisation_type('minimise')
        games = self._select_training_games()
        o.prepare_offensive_games(games)
        result = o.optimise()
        self._update_heuristics(result[:-1], self.map_type)
        self._reset_training_performance()

    # Based on the distribution of land and no-land games in the training data, choose a specific weighted variant.
    def _select_training_games(self):

        games = self.opponent_profile['games']
        game_count = min(len(games), gc.MAX_GAMES_LOGGED_PER_OPPONENT)
        selection = min(len(games), GAME_COUNT)
        stored_games = sorted(games, reverse=True)[:game_count]
        print(len([g for g in stored_games if games[g]['map_type'] == self.map_type][:selection]))
        return [g for g in stored_games if games[g]['map_type'] == self.map_type][:selection]

    def _update_heuristics(self, values, map_type):

        # Set newly found heuristic values
        for name, val in zip(self.heuristic_choices, values):
            if name not in self.opponent_profile['heuristics']:
                self.opponent_profile['heuristics'][name] = {}

            if map_type in self.opponent_profile['heuristics'][name]:
                print('Replacing', map_type, 'heuristic', '\'' + name + '\'', 'of value',
                      self.opponent_profile['heuristics'][name][map_type], 'with:', val)
            else:
                print('Setting', map_type, 'heuristic', '\'' + name + '\'', 'with:', val)
            self.opponent_profile['heuristics'][name][map_type] = val

    # Add the current game (has to have ended) to the bot's opponent profile.
    def _add_game_to_profile(self, game_state, won):

        performance = self._assess_game_performance(game_state)

        self.opponent_profile['games'][self.game_id] = performance['games']

        # Ascertain if the game was actually won or not.
        self.opponent_profile['games'][self.game_id].update({'victory': won})

        # Tag game as either land or no land for later analysis.
        self.opponent_profile['games'][self.game_id].update({'map_type': self.map_type})

        # Add list of heuristics and values used to game and update training performance info.
        if self._bot_has_heuristics():
            self._update_training_performance(performance)
            self.opponent_profile['games'][self.game_id].update({'heuristics': self.heuristic_info})

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

    # Measure how well a game went since the last training.
    def _update_training_performance(self, last_performance):

        # If we have not trained the bot, initialise the metrics to track.
        if 'games_since_training' not in self.opponent_profile['misc']:
            self.opponent_profile['misc']['games_since_training'] = {}
            self.opponent_profile['misc']['accuracy_before_training'] = {}
            self.opponent_profile['misc']['accuracy_after_training'] = {}

            if self.map_type not in self.opponent_profile['misc']['games_since_training']:
                self.opponent_profile['misc']['games_since_training'][self.map_type] = 1
                self.opponent_profile['misc']['accuracy_before_training'][self.map_type] = 0
                self.opponent_profile['misc']['accuracy_after_training'][self.map_type] = last_performance['games'][
                    'accuracy']

        # Update the game count and average accuracy incrementally.
        else:
            self.opponent_profile['misc']['games_since_training'][self.map_type] += 1
            previous_accuracy = self.opponent_profile['misc']['accuracy_after_training'][self.map_type]
            new_accuracy = last_performance['games']['accuracy']
            games_in_avg = self.opponent_profile['misc']['games_since_training'][self.map_type]
            self.opponent_profile['misc']['accuracy_after_training'][self.map_type] = \
                previous_accuracy + (new_accuracy - previous_accuracy) / games_in_avg

    def _reset_training_performance(self):
        self.opponent_profile['misc']['games_since_training'][self.map_type] = 0
        self.opponent_profile['misc']['accuracy_before_training'][self.map_type] = \
            self.opponent_profile['misc']['accuracy_after_training'][self.map_type]
        self.opponent_profile['misc']['accuracy_after_training'][self.map_type] = 0

    # Generates an empty opponent profile.
    def _generate_profile(self):
        print('\nBot', self.bot.bot_name, 'has not played', self.opponent_name, 'before.')
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
            win_str = 'Win rate: ' + '{:.3f}'.format(avg_wins * 100) + '%'

            map_wins = [game['victory'] for game in game_stats if game['map_type'] == self.map_type]
            if map_wins:
                avg_map_wins = map_wins.count(True) / len(map_wins)
                win_str += '     ' + self.map_type + ': ' + '{:.3f}'.format(avg_map_wins * 100) + '%'

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


def is_game_over(game_state):
    # If no game_state is actually given.
    if not game_state:
        return False

    ships = game_state['Ships']
    player_board = game_state['MyBoard']
    opp_board = game_state['OppBoard']

    # If at least one side has no more ships left.
    return len(board_info.ships_still_afloat(ships, player_board)) == 0 \
           or len(board_info.ships_still_afloat(ships, opp_board)) == 0
