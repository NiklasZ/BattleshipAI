# This module handles all the activities around a bot such as loading it, logging and tracking its performance and
# also training heuristics for it.

# project imports.
import src.ai.board_info as board_info
import src.utils.file_io as io
import src.ai.heuristics as heur
import src.ai.bot_learning as bot_learn
import src.utils.game_recorder as gc
# library imports.
import importlib
import numpy as np

PLUGIN_PATH = 'src.ai.bots'  # this is the module path where the AI searches for bots to use.
TRAIN_INTERVAL = 50  # Consider training after this many games have been played against an opponent.
GAME_COUNT = 20  # Default number of games to train.
MAX_GAMES_WITHOUT_TRAINING = 200  # Force a training session after this many games have elapsed against the opponent.
UNDERPERFOMANCE_THRESHOLD = 0.1  # By how much a trained bot has to underperform to be retrained at a training interval.


class AI:
    """
    This class is used to load bots, logging and tracking their performance vs an opponent and training. Of particular
    importance to this class is the self.opponent_profile. It is a dictionary that contains all information about games
    between the chosen bot and a specific opponent. It has a structure as follows:

        {'bot_name': self.bot.bot_name,
        opponent_name': self.opponent_name,
        'games': {more info about each game played},
        'heuristics': {heuristics the bot has trained},
        'misc': {miscellaneous meta-data}}

        Respectively the nested dictionaries hold:

        'games':{game_id provided by aigaming: {game_stats},...}
        Here a single element game_stats contains:
        {'accuracy': bot's accuracy during tha game, 'evasion': bot's evasion during the game, 'victory': True or False
        depending on whether the bot won the game, 'map_type': type of map the bot played on, 'heuristics':[list of
        heuristic and value pairs used in the game]}

        'heuristics':{name of a heuristic:{map_type: heuristic value},...}

        'misc':{'games_since_training': number of games since last training, 'accuracy_before_training': bot accuracy
        prior to training, 'accuracy_after_training': accuracy after training}.
    """

    def __init__(self, game_state):
        self.bot = None  # the bot to use
        self.opponent_profile = None  # a dictionary of the opponent's data.
        self.opponent_name = game_state['OpponentId']
        self.game_id = game_state['GameId']
        self.heuristic_info = None  # list containing (heuristic name, value) used by bot during play.
        self.heuristic_choices = None  # list of heuristic names requested to play & train.
        self.bot_location = None  # module path to the bot.
        # Determine whether the map is land map or one with just water.
        if board_info.is_there_land(np.array(game_state['MyBoard'])):
            self.map_type = 'land'
        else:
            self.map_type = 'no-land'

    def load_bot(self, name, heuristic_choices=None):
        """
        This function loads a bot based based on the provided name. It will also load the profile between the opponent
        and bot. If said profile does not exist, it generates a blank one. Finally, it also checks what heuristics
        are specified and sets them for the bot. to use.
        :param name: name of the bot.
        :param heuristic_choices: a list of heuristic names.
        :return:
        """
        self.opponent_profile = io.load_profile(name, self.opponent_name)
        self.heuristic_choices = heuristic_choices
        self.display_play_stats()  # Displays play-time stats in the console.

        self.bot_location = PLUGIN_PATH + '.' + name
        # Gets the class Bot and creates an instance of it.
        self.bot = getattr(importlib.import_module(self.bot_location), 'Bot')()

        if not self.opponent_profile:
            self._generate_profile()

        # Check if there are heuristics specified to use and whether the bot actually supports heuristics.
        if heuristic_choices:
            if self._bot_has_heuristics():
                self._load_heuristics(heuristic_choices)
            else:
                print('Bot', self.bot.bot_name, 'does not use heuristics and is not trainable.')

    def make_decision(self, game_state):
        """
        This function decides to either return a ship placement or the next move from the bot, based on what the
        game_state specifies.
        :param game_state: a game_state dictionary containing all information about the game's current state. This is
        as specified by aigaming under https://help.aigaming.com/bat-quickref.
        :return: a dictionary of either ship placements or a move.
        """
        if game_state['Round'] == 0:
            return self.bot.place_ships(game_state)
        else:
            return self.bot.make_move(game_state)

    def finish_game(self, game_state, won, train_bot=False):
        """
        This function is to be called after a game is finished to get the gameplay stats, assess the bot's performance
        and decide whether to train it.
        :param game_state: an aigaming game_state dictionary (should be the last game state).
        :param won: a boolean that specifies whether the game was won or not.
        :param train_bot: optional parameter that specifies whether the bot should consider training.
        :return:
        """

        self._add_game_to_profile(game_state, won)  # adds game to opponent profile.

        # If we want to train the bot AND the bot can actually be trained AND the ai deems it worthwhile to train
        # the bot, the bot is trained.
        if train_bot and self._bot_has_heuristics() and self._decide_whether_to_train():
            self._train_bot()
        # Save training results and added game.
        io.save_profile(self.opponent_profile, self.bot.bot_name, self.opponent_name)

    def _bot_has_heuristics(self):
        """
        Checks whether the bot has a function that allows it to set heuristics and accordingly determines whether it
        can use them or not.
        :return:
        """
        set_heuristics = getattr(self.bot, "set_heuristics", None)
        return callable(set_heuristics)

    def _load_heuristics(self, heuristic_names):
        """
        Given a list of heuristic names, this function checks if the bot has trained on them and if so, loads them
        into the bot.
        :param heuristic_names: a list of heuristic names.
        :return:
        """
        set_heuristics = getattr(self.bot, "set_heuristics", None)
        heuristics = []
        self.heuristic_info = []
        # For each heuristic, load the respective function and weight.
        for name in heuristic_names:

            # Check if a this heuristic has ever been set and if not, skip it.
            if name not in self.opponent_profile['heuristics']:
                print('Bot', self.bot.bot_name, 'has not trained', name, 'yet.')
                continue

            heuristic_func = getattr(heur, name)  # get the heuristic function

            # Try to load the heuristic relevant to the map type.
            if self.map_type in self.opponent_profile['heuristics'][name]:
                heuristic_val = self.opponent_profile['heuristics'][name][self.map_type]

                self.heuristic_info.append((name, heuristic_val))
                print('Loading a', self.map_type, 'heuristic:', '\'' + name + '\'', 'of value', heuristic_val)
                heuristics.append((heuristic_func, heuristic_val))

            else:
                print('Bot', self.bot.bot_name, 'has not trained', name, 'for', self.map_type, 'maps yet.')
        # Set the heuristics for the bot.
        set_heuristics(heuristics)

    def _decide_whether_to_train(self):
        """
        This function decides based on the defined constants and availability of games, whether to train or not. Each
        condition is essentially a rule to check against and the function will print out its decision.
        :return:
        """
        # If we are not at a training interval, do not train.
        remainder = len(self.opponent_profile['games']) % TRAIN_INTERVAL
        if remainder != 0:
            print('No training as the training interval has not been reached. Will attempt after',
                  TRAIN_INTERVAL - remainder, 'game(s).')
            return False

        # If there are not enough games to train yet for a map type, do not train.
        map_type_count = len(self._select_training_games())
        if map_type_count < GAME_COUNT:
            print('No training as there are not enough games of type', self.map_type + '. Have: ' +
                  str(map_type_count) + '. Require:', GAME_COUNT)
            return False

        # If we have never trained a chosen heuristic, do train.
        trained_heuristics = set(self.opponent_profile['heuristics'].keys())
        chosen_heuristics = set(self.heuristic_choices)
        if trained_heuristics != chosen_heuristics:
            print('Will commence training as', self.bot.bot_name, 'has not trained all chosen heuristics.')
            return True

        # If a heuristic has never been trained with a map type, do train.
        for heuristic in self.opponent_profile['heuristics']:
            if self.map_type not in self.opponent_profile['heuristics'][heuristic]:
                print('Will commence training as', self.bot.bot_name, 'has not trained', heuristic, 'on a',
                      self.map_type, 'map.')
                return True

        # If we have not trained for MAX_GAMES_WITHOUT_TRAINING or more, do train.
        if self.opponent_profile['misc']['games_since_training'][self.map_type] >= MAX_GAMES_WITHOUT_TRAINING:
            print('Will commence training as', self.bot.bot_name, 'has not been trained on', self.map_type, 'in',
                  self.opponent_profile['misc']['games_since_training'][self.map_type], 'games.')
            return True

        # If the current accuracy has sufficiently underperformed vs the one prior to training, do train.
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

        # Under normal circumstances, this point should not be reached.
        return False

    def _train_bot(self):
        """
        This function prepares the training algorithm for a bot. It begins by setting various training parameters,
        then starting the training and finally storing the result. Note: the AI will always attempt to train on the map
        type it has under self.map_type (typically the last played one).
        :return:
        """
        o = bot_learn.Optimiser(self.bot.bot_name, self.opponent_name, self.bot_location)  # initialise optimiser
        o.prepare_heuristics(self.heuristic_choices)  # set heuristics to train.
        o.set_optimisation_type('minimise')  # set whether to minimise or maximise the evaluation function.
        games = self._select_training_games()  # get game ids to train on.
        o.prepare_offensive_games(games)  # load them into the optimiser.
        result = o.optimise()  # run the optimiser.
        self._update_heuristics(result[:-1], self.map_type)  # store heuristics.
        self._reset_training_performance()  # reset training stats to monitor performance of latest train.

    def _select_training_games(self):
        """
        This function chooses the ids of the games that a bot should be trained on. It decides this based on specified
        constants and what games are available and of the right map type.
        :return: a list of game ids
        """
        games = self.opponent_profile['games'] # get games
        # count of how many games we actually have stored.
        game_count = min(len(games), gc.MAX_GAMES_LOGGED_PER_OPPONENT)
        # get the ids of games we actually have stored (by recency).
        stored_games = sorted(games, reverse=True)[:game_count]
        # Get the stored games that actually are of the desired map type.
        map_games = [g for g in stored_games if games[g]['map_type'] == self.map_type]
        # Return the mapped games, capped by the GAME_COUNT needed for training.
        selection = min(len(map_games), GAME_COUNT)

        return map_games[:selection]

    def _update_heuristics(self, values, map_type):
        """
        This function updates the heuristics in the opponent_profile after training.
        :param values: a list of heuristic weights (assumed to be in same order as heuristic names).
        :param map_type: a string that holds the type of map the heuristics were trained on.
        :return:
        """
        # Iterate through each heuristic name and weight.
        for name, val in zip(self.heuristic_choices, values):
            # If we have never set the heuristic before, create the dictionary to hold it.
            if name not in self.opponent_profile['heuristics']:
                self.opponent_profile['heuristics'][name] = {}

            # Choose respective text to either set or update the heuristic.
            if map_type in self.opponent_profile['heuristics'][name]:
                print('Replacing', map_type, 'heuristic', '\'' + name + '\'', 'of value',
                      self.opponent_profile['heuristics'][name][map_type], 'with:', val)
            else:
                print('Setting', map_type, 'heuristic', '\'' + name + '\'', 'with:', val)
            # Set the heuristic.
            self.opponent_profile['heuristics'][name][map_type] = val

    def _add_game_to_profile(self, game_state, won):
        """
        Adds the latest played game to the opponent_profile. These are kept for displaying and monitoring bot
        performance against certain opponents.
        :param game_state: an aigaming game_state dictionary (should be the last game state).
        :param won: a boolean that specifies whether the game was won or not.
        :return:
        """

        performance = self._assess_game_performance(game_state) # get metrics of how well the game went for the bot.

        self.opponent_profile['games'][self.game_id] = performance

        # Store if the game was actually won or not.
        self.opponent_profile['games'][self.game_id].update({'victory': won})

        # Tag game as either land or no land for later analysis.
        self.opponent_profile['games'][self.game_id].update({'map_type': self.map_type})

        # Add list of heuristics and values used to game and update training performance info.
        if self._bot_has_heuristics():
            self._update_training_performance(performance)
            self.opponent_profile['games'][self.game_id].update({'heuristics': self.heuristic_info})

    def _assess_game_performance(self, final_state):
        """
        Calculates how well the bot played. It takes any performance metrics the bot has itself and also keeps measures
        of:
        the bot's accuracy = (hits/(hits+misses)
        the bot's evasion  = 1 - opponent's accuracy
        :param final_state: an aigaming game_state dictionary (should be the last game state).
        :return: a dictionary containing performances. It has the form:
        {'accuracy': accuracy, 'evasion': evasion,.... any other metrics defined by the bot}
        """
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

        performance.update({'accuracy': accuracy, 'evasion': evasion})

        return performance

    def _update_training_performance(self, last_performance):
        """
        This function updates the training performance of the bot before and after training to enable tracking of its
        performance.
        :param last_performance: a dictionary containing performances. It has the form:
        {'accuracy': accuracy, 'evasion': evasion,.... any other metrics defined by the bot}
        :return:
        """

        # If we have never tracked the bot, initialise the metrics to track.
        if 'games_since_training' not in self.opponent_profile['misc']:
            self.opponent_profile['misc']['games_since_training'] = {}
            self.opponent_profile['misc']['accuracy_before_training'] = {}
            self.opponent_profile['misc']['accuracy_after_training'] = {}

        # If we have never tracked the bot for a map type, set the performance as the one of the last game.
        if self.map_type not in self.opponent_profile['misc']['games_since_training']:
            self.opponent_profile['misc']['games_since_training'][self.map_type] = 1
            self.opponent_profile['misc']['accuracy_before_training'][self.map_type] = 0
            self.opponent_profile['misc']['accuracy_after_training'][self.map_type] = last_performance['accuracy']

        # Otherwise we are currently tracking the bot after some training.
        else:
            # Increment the games played since training.
            self.opponent_profile['misc']['games_since_training'][self.map_type] += 1
            previous_accuracy = self.opponent_profile['misc']['accuracy_after_training'][self.map_type]
            new_accuracy = last_performance['accuracy']
            games_in_avg = self.opponent_profile['misc']['games_since_training'][self.map_type]
            # Update the bot's average accuracy after training incrementally.
            self.opponent_profile['misc']['accuracy_after_training'][self.map_type] = \
                previous_accuracy + (new_accuracy - previous_accuracy) / games_in_avg

    def _reset_training_performance(self):
        """
        Resets the training tracking of a bot just after it has been trained. The current performance is updated to be
        the previous performance.
        :return:
        """
        self.opponent_profile['misc']['games_since_training'][self.map_type] = 0
        self.opponent_profile['misc']['accuracy_before_training'][self.map_type] = \
            self.opponent_profile['misc']['accuracy_after_training'][self.map_type]
        self.opponent_profile['misc']['accuracy_after_training'][self.map_type] = 0

    def _generate_profile(self):
        """
        Generates a dictionary holding a barebones profile of the bot and opponent.
        :return:
        """
        print('\nBot', self.bot.bot_name, 'has not played', self.opponent_name, 'before.')
        self.opponent_profile = {'bot_name': self.bot.bot_name,
                                 'opponent_name': self.opponent_name,
                                 # Contains mapping of game_id:[interesting statistics about the game]
                                 'games': {},
                                 # Contains current heuristic values to use for the opponent.
                                 'heuristics': {},
                                 # Anything else.
                                 'misc': {}}

    def display_play_stats(self):
        """
        This function display past play-time stats between the bot and an opponent. It will of course, only do this
        if they have a playing history. The stats it displays are:

        games played against each other
        win rate
        win rate on current map type
        accuracy and evasion
        accuracy and evasion on current map type

        Note: a lot of this information is re-calculated from the opponent_profile rather than cached,
        so this function can become slower as the opponent profile grows in games.

        :return:
        """
        if self.opponent_profile:
            # Print banner
            print('\n---', self.opponent_profile['bot_name'], 'vs:', self.opponent_profile['opponent_name'], '---')

            game_stats = self.opponent_profile['games'].values()
            print('Games played:', len(game_stats))

            # Calculate win rate
            wins = [game['victory'] for game in game_stats]
            avg_wins = wins.count(True) / len(wins)
            win_str = 'Win rate: ' + '{:.3f}'.format(avg_wins * 100) + '%'

            map_wins = [game['victory'] for game in game_stats if game['map_type'] == self.map_type]
            if map_wins:
                avg_map_wins = map_wins.count(True) / len(map_wins)
                win_str += '     ' + self.map_type + ': ' + '{:.3f}'.format(avg_map_wins * 100) + '%'

            print(win_str)

            # Calculate accuracy and evasion.
            avg_accuracy = np.average([game['accuracy'] for game in game_stats])
            avg_evasion = np.average([game['evasion'] for game in game_stats])
            print('Average accuracy:', '{:.3f}'.format(avg_accuracy * 100) + '%     ',
                  'Average evasion:', '{:.3f}'.format(avg_evasion * 100) + '%')

            avg_map_accuracies = [g['accuracy'] for g in game_stats if g['map_type'] == self.map_type]
            avg_map_evasions = [g['evasion'] for g in game_stats if g['map_type'] == self.map_type]

            # In case this is the first game on this type of map, do not show any performances.
            if avg_map_accuracies and avg_map_evasions:
                avg_map_accuracy = np.average(avg_map_accuracies)
                avg_map_evasion = np.average(avg_map_evasions)
                print('Average', self.map_type, 'accuracy:', '{:.3f}'.format(avg_map_accuracy * 100) + '%     ',
                      'Average', self.map_type, 'evasion:', '{:.3f}'.format(avg_map_evasion * 100) + '%')
            print()


def is_game_over(game_state):
    """
    This is a function that based on the game_state tries to determine whether a game was actually finished or not. It
    does this by first determining if the given game_state exists and then otherwise if at least one board has all ships
    sunk.
    :param game_state: an aigaming game_state dictionary (should be the last game state).
    :return: False if the game is not over and True otherwise.
    """
    # If no game_state is actually given.
    if not game_state:
        return False

    ships = game_state['Ships']
    player_board = game_state['MyBoard']
    opp_board = game_state['OppBoard']

    # If at least one side has no more ships left.
    return len(board_info.ships_still_afloat(ships, player_board)) == 0 \
           or len(board_info.ships_still_afloat(ships, opp_board)) == 0
