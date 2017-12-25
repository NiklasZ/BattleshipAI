import src.ai.ai_helpers as ai_help
import src.utils.fileIO as io
import src.ai.ai as ai
import src.utils.game_simulator as sim
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

    def load_bot(self):
        location = ai.PLUGIN_PATH + '.' + self.bot_name
        # Gets the class Bot and creates an instance of it.
        self.bot = getattr(importlib.import_module(location), 'Bot')()

    # Load the respective functions for each chosen heuristic.
    def prepare_heuristics(self, chosen_heuristics):
        for h in chosen_heuristics:
            self.heuristic_names.append(h)
            self.heuristics.append([getattr(self, h)])

    def save_heuristics(self):
        pass

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
            simulation = sim.GameSimulator(self.bot_name, None, game['opp_board'], game['ships'])
            simulation.attack_until_win()
            result = ai_help.count_hits_and_misses(simulation.opponent_masked_board)
            hits.append(result['hits'])
            misses.append(result['misses'])

        if self.optimisation_type == 'minimise':
            return misses
        if self.optimisation_type == 'maximise':
            return np.average(np.divide(hits,misses))

    def optimise(self):
        pass

    def set_optimisation_type(self, type):
        self.optimisation_type = type

# Function that creates targeting scores using provided heuristics.
# Each heuristic is provided as a tuple of (function, args) in a list.
def get_targeting_scores(opp_board, opp_ships, heuristics):
    scores = np.zeros((len(opp_board), len(opp_board[0])), dtype=float)  # final scores
    cell_modifiers = np.ones((len(opp_board), len(opp_board[0])), dtype=float)  # modifiers to apply to cell.
    ship_modifiers = {}  # modifiers to apply to ship.
    # A dict of coordinates and their valid ship alignments. This is useful as some heuristics will need to have
    # full alignment data to make decisions.
    ship_sets = {}
    # A dict of non-redundant coordinates and valid ship alignments. Useful to avoid weighting pointless positions.
    reduced_ship_sets = {}
    # y is the row, x is the column
    for (y, x), val in np.ndenumerate(opp_board):
        if val == '':
            ship_alignments = ai_help.alignments_in(y, x, opp_board, opp_ships)
            ship_sets[(y, x)] = ship_alignments
            ai_help.reduce_alignments(y, x, reduced_ship_sets, ship_alignments)

            for ship in ship_alignments:
                ship_modifiers[ship] = 1

    # Run each heuristic to modify the scores.
    for heuristic in heuristics:
        heuristic[0](cell_modifiers, ship_modifiers, ship_sets, opp_board, heuristic[1])

    # Apply resulting weights.
    for (y, x), val in np.ndenumerate(scores):
        # Account for non-available coordinates.
        if (y, x) in reduced_ship_sets:
            for ship in reduced_ship_sets[(y, x)]:
                scores[y, x] += ship_modifiers[ship]
            scores[y, x] *= cell_modifiers[y, x]

    return scores


# Applies a heuristic on potential ships that would be adjacent to known ships.
# Depending on adj_weight this will either prioritise adjacent ships or neglect them.


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
