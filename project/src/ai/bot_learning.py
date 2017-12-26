import src.ai.ai_helpers as ai_help
import src.utils.fileIO as io
import src.ai.ai as ai
import src.utils.game_simulator as sim
import src.ai.heuristics as heur
import lib.blackbox as bb

from noisyopt import minimizeCompass
from noisyopt import minimizeSPSA
import copy
import importlib
import numpy as np


class Optimiser:
    def __init__(self, bot_name, opponent_name):
        self.bot_name = bot_name
        self.opponent_name = opponent_name
        self.opponent_profile = io.load_profile(bot_name, self.opponent_name)
        self.bot = None
        self.games = None
        self.heuristics = []
        self.heuristic_names = []
        self.optimisation_type = None
        self.map_type = 'generic'

    def load_bot(self):
        location = ai.PLUGIN_PATH + '.' + self.bot_name
        # Gets the class Bot and creates an instance of it.
        self.bot = getattr(importlib.import_module(location), 'Bot')()

    # Load the respective functions for each chosen heuristic.
    def prepare_heuristics(self, chosen_heuristics):
        for h in chosen_heuristics:
            self.heuristic_names.append(h)
            self.heuristics.append([getattr(heur, h)])

    def save_heuristics(self, values):

        for name, val in zip(self.heuristic_names, values):

            if name not in self.opponent_profile['heuristics']:
                self.opponent_profile['heuristics'][name] = {}

            if self.map_type in self.opponent_profile['heuristics'][name]:
                print('Replacing heuristic', '\'' + name + '\'', 'of value',
                      self.opponent_profile['heuristics'][name][self.map_type], 'with:', val)
            self.opponent_profile['heuristics'][name][self.map_type] = val

        io.save_profile(self.opponent_profile, self.bot_name, self.opponent_name)

    # Chooses k most recent games and picks the initial ship data.
    def prepare_k_offensive_games(self, k):
        all_games = io.load_pickled_game_log(self.bot_name, self.opponent_name)
        # Get latest k game_states
        latest_k_entries = sorted(all_games.items(), reverse=True)[:k]
        self.games = []
        for entry in latest_k_entries:
            game_id, game_states = entry
            # Get last known board of the game.
            opp_board = extract_original_opp_board(game_states[-1]['OppBoard'])
            self.games.append({'game_id': game_id, 'opp_board': opp_board, 'ships': game_states[-1]['Ships']})

    def play_games(self, heuristic_values):
        for heuristic, val in zip(self.heuristics, heuristic_values):
            heuristic.append(val)

        misses = []
        hits = []
        for game in self.games:
            disposable_game = copy.deepcopy(game)
            simulation = sim.GameSimulator(self.bot_name, None, disposable_game['opp_board'], disposable_game['ships'],
                                           heuristics=self.heuristics)
            simulation.attack_until_win()
            result = ai_help.count_hits_and_misses(simulation.opponent_masked_board)
            hits.append(result['hits'])
            misses.append(result['misses'])

        if self.optimisation_type == 'minimise':
            #print(heuristic_values,np.sum(misses))
            return np.sum(misses)
        if self.optimisation_type == 'maximise':
            return np.sum(np.divide(hits, misses + hits))

    def optimise(self):
        boxes = []
        for name in self.heuristic_names:
            boxes.append(heur.SEARCH_RANGES[name])

        result = bb.search(f=self.play_games,  # given function
                        box=boxes,  # range of values for each parameter
                        n=20,  # number of function calls on initial stage (global search)
                        m=5,  # number of function calls on subsequent stage (local search)
                        batch=4,  # number of calls that will be evaluated in parallel
                        resfile='output.csv')  # text file where results will be saved

        # Get top parameter values.
        return result[0]

    def optimise_alt(self):
        boxes = []
        for name in self.heuristic_names:
            boxes.append(heur.SEARCH_RANGES[name])

        result = minimizeCompass(self.play_games,x0=[4],bounds=boxes,errorcontrol=True,paired=False,disp=True)
        print(result)

        return result['x']

    def optimise_alt_2(self):
        boxes = []
        for name in self.heuristic_names:
            boxes.append(heur.SEARCH_RANGES[name])

        result = minimizeSPSA(self.play_games,x0=[1],bounds=boxes,paired=False,disp=True)
        print(result)

        return result['x']

    def set_optimisation_type(self, type):
        self.optimisation_type = type


# Extract sunken ship data from an opponent to create an unused copy for training.
def extract_original_opp_board(finished_board):
    opp_board = copy.deepcopy(finished_board)
    for (y, x), val in np.ndenumerate(opp_board):
        if val in ['M', 'H']:
            opp_board[y][x] = ''
        # Only consider sunken ships. Half-finished ships (marked with 'H') are too ambiguous.
        elif len(val) == 2 and val[0] == 'S':
            opp_board[y][x] = val[1]

    return opp_board

def main():
    import os
    os.chdir('..')
    o = Optimiser('pho', 'housebot-competition')
    o.load_bot()
    o.prepare_heuristics(['ship_adjacency'])
    o.set_optimisation_type('minimise')
    o.prepare_k_offensive_games(200)
    #o.play_games([0.5])
    result = o.optimise()
    np.set_printoptions(suppress=True)
    print(result)
    #result = o.optimise_alt_2()
    o.save_heuristics(result[:-1])
    # o.save_heuristics([0.5])

if __name__ == '__main__':
    main()



