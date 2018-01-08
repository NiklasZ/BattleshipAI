# This module is used to optimise a bot's heuristics. It gets its training data from offensive_explorer and calls a
# local library for the optimisation function.
# This optimisation function was developed by Paul Knysh and can be found here: https://github.com/paulknysh/blackbox

# Project imports
import src.ai.board_info as board_info
import src.utils.file_io as io
import src.ai.heuristics as heur
import lib.blackbox as bb  # optimisation function
import src.ai.offensive_explorer as explorer

# Library imports
import copy
import numpy as np
import time

BB_GLOBAL_CALLS = 10  # Number of global search calls the black box optimisation makes.
BB_LOCAL_CALLS = 5  # Number of local search calls the black box optimisation makes.
PARALLEL_CALLS = 4  # Default number of threads that will investigate different parameters.


class Optimiser:
    """
    The optimiser class creates an object that loads a chosen bot and after some configuration, can optimise it. Due
    to the nature of the function, it is essential to specify all non-optimisable parameters beforehand. Thus, call
    in the following after initialisation:

    prepare_heuristics(heuristics): so the bot knows which heuristics to run.
    set_optimisation_type(minimise or maximise): so the evaluation function knows what to optimise towards.
    prepare_offensive_games(game ids): so the optimiser knows what games to load and optimise over.
    """

    def __init__(self, bot_name, opponent_name, bot_location):
        self.bot_name = bot_name
        self.opponent_name = opponent_name
        self.opponent_profile = io.load_profile(bot_name, self.opponent_name)  # profile as defined in ai.py
        self.bot_location = bot_location  # module location from which to load the bot.
        self.games = None  # list of game_state-like dictionaries that hold everything necessary to optimise over a game.
        self.heuristics = []  # list of heuristic functions.
        self.heuristic_names = []  # list of heuristic names.
        self.optimisation_type = None

    def prepare_heuristics(self, chosen_heuristics):
        """
        Set the heuristics to optimise over. Each must be a valid function in heuristics.py
        :param chosen_heuristics: a list of names of heuristics.
        :return:
        """
        for h in chosen_heuristics:
            self.heuristic_names.append(h)
            self.heuristics.append([getattr(heur, h)])

    def prepare_offensive_games(self, game_ids):
        """
        Load the list of stored games pick the ones with the desired game ids. Then for each one, choose the final state
        and remove all fired shots, keeping the ship positions.
        :param game_ids: A list of integer game ids for the game to load. Note that these have to be present in the
        game log or there will be errors.
        :return:
        """

        # Load serialised games
        all_games = io.load_pickled_game_log(self.bot_name, self.opponent_name)
        self.games = []

        for game_id in game_ids:
            game_states = all_games[game_id]
            # Get last known board of the game.
            opp_board = _extract_original_opp_board(game_states[-1]['OppBoard'])
            self.games.append({'game_id': game_id, 'opp_board': opp_board, 'ships': game_states[-1]['Ships']})

    def play_games(self, heuristic_values):
        """
        The function to be fed to the optimisation algorithm. It works by exploring each game and counting the hits and
        misses in the terminal state, effectively measuring accuracy. It then averages them for the game and moves on
        to the next one. At the end, it then averages the hits and misses overall and depending on whether we want to
        maximise or minimise the score of the function, we return the following:

        minimise: the average number of misses
        maximise: the accuracy (hits/(misses+hits))
        :param heuristic_values: a list of heuristic values that the optimisation algorithm chooses to test.
        :return: a floating number representing a score.
        """

        # Pair each heuristic function with the respective weight.
        for heuristic, val in zip(self.heuristics, heuristic_values):
            heuristic.append(val)

        misses = [] # list of average miss counts per game
        hits = [] # list of average hit counts per game

        for game in self.games:
            disposable_game = copy.deepcopy(game) # Need to copy this as this function will be called multiple times.
            # Call for the explorer to explore this board's game tree.
            sampled_games = explorer.init_bfs(self.bot_location, self.heuristics, disposable_game['opp_board'],
                                              disposable_game['ships'], explorer.BOARD_SAMPLES)
            sampled_misses = []
            sampled_hits = []

            # Average the misses & hits for a game.
            for s_g in sampled_games:
                result = board_info.count_hits_and_misses(s_g)
                sampled_misses.append(result['misses'])
                sampled_hits.append(result['hits'])

            misses.append(np.average(sampled_misses))
            hits.append(np.average(sampled_hits))

        # Choose which score to return based on optimisation type.
        if self.optimisation_type == 'minimise':
            return np.average(misses)
        if self.optimisation_type == 'maximise':
            return np.average(np.divide(hits, misses + hits))

    def optimise(self):
        """
        This function makes the call to the optimisation algorithm black-box. The details of how it works can be found
        on the creator's page: https://github.com/paulknysh/blackbox.
        :return:
        """
        boxes = []
        for name in self.heuristic_names:
            boxes.append(heur.SEARCH_RANGES[name])

        start = time.time()
        print('Starting optimisation of:', ','.join(self.heuristic_names))
        result = bb.search(f=self.play_games,  # given function
                           box=boxes,  # range of values for each parameter
                           n=BB_GLOBAL_CALLS,  # number of function calls on initial stage (global search)
                           m=BB_LOCAL_CALLS,  # number of function calls on subsequent stage (local search)
                           batch=PARALLEL_CALLS,  # number of calls that will be evaluated in parallel
                           resfile='output.csv')  # text file where results will be saved

        print('Completed after', '{:.3f}'.format(time.time() - start) + 's')

        # Get top parameter values.
        return result[0]

    def set_optimisation_type(self, type):
        """
        Sets whether to the optimisation function should maximise or minimise.
        :param type: a string that should be either 'minimise' or 'maximise'.
        :return:
        """
        self.optimisation_type = type



def _extract_original_opp_board(finished_board):
    """
    This function removes all shots that have been fired on it, reverting sunken ships to normal. Notably, coordinates
    that have hits, but no sunk ship will be set to be empty as the position of the original ship is unclear. The
    motivation for this function is to make past games against opponents replayable. However, as the opponent's
    positions are never revealed unless hits, instances where not all ships are sunk will be incomplete.
    :param finished_board:
    :return:
    """
    opp_board = copy.deepcopy(finished_board) # copy the board.
    for (y, x), val in np.ndenumerate(opp_board):
        if val in ['M', 'H']: # Modify all hits and misses to blanks.
            opp_board[y][x] = ''
        # Only consider sunken ships. Half-finished ships (marked with 'H') are too ambiguous.
        elif len(val) == 2 and val[0] == 'S':
            opp_board[y][x] = val[1]

    return opp_board


# This is old testing code.
# def main():
#     bot_location = 'src.ai.bots' + '.pho'
#     o = Optimiser('pho', 'housebot-competition', bot_location)
#     game_dict = o.opponent_profile['games']
#     games = [g for g in sorted(game_dict, reverse=True)[:10]]
#     o.set_optimisation_type('minimise')
#     o.prepare_offensive_games(games)
#     o.prepare_heuristics(['ship_adjacency'])
#     result = o.optimise()
#     print('\nChosen parameters:', result)
#
#
# if __name__ == "__main__":
#     main()
