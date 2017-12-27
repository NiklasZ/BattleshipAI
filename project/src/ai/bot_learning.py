import src.ai.board_info as board_info
import src.utils.fileIO as io
import src.utils.game_simulator as sim
import src.ai.heuristics as heur
import lib.blackbox as bb

import copy
import numpy as np
import time

BB_GLOBAL_CALLS = 10 # Number of global search calls the black box optimisation makes.
BB_LOCAL_CALLS = 5 # Number of local search calls the black box optimisation makes.
GAME_COUNT = 100 # Default number of games the optimiser uses.
REPLAYS = 5 # Default number ot times each game is played.
PARALLEL_CALLS = 4 # Default number of threads that will investigate different parameters.

class Optimiser:
    def __init__(self, bot_name, opponent_name, bot_location):
        self.bot_name = bot_name
        self.opponent_name = opponent_name
        self.opponent_profile = io.load_profile(bot_name, self.opponent_name)
        self.bot_location = bot_location
        self.games = None
        self.heuristics = []
        self.heuristic_names = []
        self.optimisation_type = None
        self.map_type = 'generic'
        self.replay_games = REPLAYS  # Number of times to replay a game. This is to better sample bot's random decisions.

    # Load the respective functions for each chosen heuristic.
    def prepare_heuristics(self, chosen_heuristics):
        for h in chosen_heuristics:
            self.heuristic_names.append(h)
            self.heuristics.append([getattr(heur, h)])

    # Chooses the games to play, based on a list of game_ids.
    def prepare_offensive_games(self, game_ids):
        all_games = io.load_pickled_game_log(self.bot_name, self.opponent_name)
        self.games = []
        for game_id in game_ids:
            game_states = all_games[game_id]
            # Get last known board of the game.
            opp_board = _extract_original_opp_board(game_states[-1]['OppBoard'])
            self.games.append({'game_id': game_id, 'opp_board': opp_board, 'ships': game_states[-1]['Ships']})

    def play_games(self, heuristic_values):
        for heuristic, val in zip(self.heuristics, heuristic_values):
            heuristic.append(val)

        misses = []
        hits = []
        for game in self.games:
            for i in range(self.replay_games):
                disposable_game = copy.deepcopy(game)
                simulation = sim.GameSimulator(self.bot_location, None, disposable_game['opp_board'],
                                               disposable_game['ships'],
                                               heuristics=self.heuristics)
                simulation.attack_until_win()
                result = board_info.count_hits_and_misses(simulation.opponent_masked_board)
                hits.append(result['hits'])
                misses.append(result['misses'])

        if self.optimisation_type == 'minimise':
            # print(heuristic_values,np.sum(misses))
            return np.average(misses)
        if self.optimisation_type == 'maximise':
            return np.average(np.divide(hits, misses + hits))

    def optimise(self):
        boxes = []
        for name in self.heuristic_names:
            boxes.append(heur.SEARCH_RANGES[name])

        start = time.time()
        print('Starting optimisation of:',','.join(self.heuristic_names))

        result = bb.search(f=self.play_games,  # given function
                           box=boxes,  # range of values for each parameter
                           n=BB_GLOBAL_CALLS,  # number of function calls on initial stage (global search)
                           m=BB_LOCAL_CALLS,  # number of function calls on subsequent stage (local search)
                           batch=PARALLEL_CALLS,  # number of calls that will be evaluated in parallel
                           resfile='output.csv')  # text file where results will be saved

        print('Completed after', '{:10.3f}'.format(time.time() - start) + 's')

        # Get top parameter values.
        return result[0]

    def set_optimisation_type(self, type):
        self.optimisation_type = type

    def set_replay_count(self, amount):
        self.replay_games = amount


# Extract sunken ship data from an opponent to create an unused copy for training.
def _extract_original_opp_board(finished_board):
    opp_board = copy.deepcopy(finished_board)
    for (y, x), val in np.ndenumerate(opp_board):
        if val in ['M', 'H']:
            opp_board[y][x] = ''
        # Only consider sunken ships. Half-finished ships (marked with 'H') are too ambiguous.
        elif len(val) == 2 and val[0] == 'S':
            opp_board[y][x] = val[1]

    return opp_board

