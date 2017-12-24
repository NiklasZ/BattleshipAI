import importlib
import numpy as np

import src.ai.ai_helpers as ai_help
import src.utils.fileIO as io
import src.ai.bot_learning as bot_learn

# TODO make this dynamic rather than fixed.
PLUGIN_PATH = 'src.ai.bots' # this is lazy but writing it dynamically is too much of a pain right now.

class AI:

    def __init__(self, game_state):
        self.bot = None
        self.opponent_profile = None
        self.opponent_name = game_state['OpponentId']
        self.game_id = game_state['GameId']
        if ai_help.is_there_land(np.array(game_state['MyBoard'])):
            self.map_type = 'land'
        else:
            self.map_type = 'no land'

    # Receive the name of a bot module to load from the 'bots' sub-folder.
    # Class name needs to be "Bot" to be found.
    def load_bot(self, name, heuristic_choices=None):
        self.opponent_profile = io.load_profile(name, self.opponent_name)
        self.display_play_stats()

        location = PLUGIN_PATH + '.' + name
        # Gets the class Bot and creates an instance of it.
        self.bot = getattr(importlib.import_module(location), 'Bot')()
        print("Loading bot:", self.bot.bot_name)

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
        set_heuristics = getattr(self.bot, "set_heuristics",None)
        # Check if the bot has a heuristics setting function.
        if callable(set_heuristics):
            heuristics = []
            # For each heuristic, load the respective function and weight.
            for name in heuristic_names:
                heuristic_func = getattr(bot_learn, name)
                # Try to load the heuristic relevant to the map type.
                if self.map_type in self.opponent_profile['heuristics'][name]:
                    heuristic_val = self.opponent_profile['heuristics'][name][self.map_type]
                # Load a generic heuristic
                else:
                    heuristic_val = self.opponent_profile['heuristics'][name]['general']

                heuristics.append((heuristic_func, heuristic_val))

            # Set the heuristics for the bot.
            set_heuristics(heuristics)

    # Add the current game (has to have ended) to the bot's opponent profile.
    def add_game_to_profile(self, game_state, won):
        if not self.opponent_profile:
            self.generate_profile()

        performance = self.assess_game_performance(game_state)
        self.opponent_profile['games'][self.game_id] = performance['games']

        # Ascertain if the game was actually won or not.
        self.opponent_profile['games'][self.game_id].update({'victory': won})

        # Tag game as either land or no land for later analysis.
        self.opponent_profile['games'][self.game_id].update({'map_type': self.map_type})

        io.save_profile(self.opponent_profile, self.bot.bot_name, self.opponent_name)

    # Measure how well a game went.
    def assess_game_performance(self, final_state):
        performance = {}

        # If the bot has any performance metrics, get those.
        get_bot_performance = getattr(self.bot, 'get_performance_metrics', None)
        if callable(get_bot_performance):
            performance = get_bot_performance(final_state)

        # Additionally, get general accuracy/evasion metrics.
        bot_stats = ai_help.count_hits_and_misses(final_state['MyBoard'])
        opp_stats = ai_help.count_hits_and_misses(final_state['OppBoard'])

        accuracy = opp_stats['hits'] / (opp_stats['hits'] + opp_stats['misses'])
        evasion = 1 - bot_stats['hits'] / (opp_stats['hits'] + opp_stats['misses'])

        metrics = {'accuracy': accuracy, 'evasion': evasion}
        if 'games' in performance:
            performance['games'].update(metrics)
        else:
            performance.update({'games': metrics})

        return performance

    # Generates an empty opponent profile.
    def generate_profile(self):
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
            game_stats = self.opponent_profile['games'].values()

            wins = [game['victory'] for game in game_stats]
            avg_wins = wins.count(True) / len(wins)

            accuracies = [game['accuracy'] for game in game_stats]
            avg_accuracy = np.average(accuracies)

            evasions = [game['evasion'] for game in game_stats]
            avg_evasion = np.average(evasions)

            print('\n---', self.opponent_profile['bot_name'], 'vs:', self.opponent_profile['opponent_name'], '---')
            print('Games played:', len(game_stats))
            print('Win rate:', '{:10.3f}'.format(avg_wins * 100) + '%')
            print('Average accuracy:', '{:10.3f}'.format(avg_accuracy * 100) + '%     ',
                  'Average evasion:', '{:10.3f}'.format(avg_evasion * 100) + '%\n')
