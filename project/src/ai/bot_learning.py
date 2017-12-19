import src.ai.ai_helpers as ai_help
import numpy as np


def learn_offensive_heuristics():
    pass


# Function that creates targeting scores using provided heuristics.
# Each heuristic is provided as a tuple of (function, args) in a list.
def get_targeting_scores(opp_board, opp_ships, heuristics=[]):
    scores = np.zeros((len(opp_board), len(opp_board[0])), dtype=int)  # final scores
    cell_modifiers = np.ones((len(opp_board), len(opp_board[0])), dtype=float)  # modifiers to apply to cell.
    ship_modifiers = {}  # modifiers to apply to ship.
    # A dict of coordinates and their valid ship alignments.
    ship_sets = {}
    # y is the row, x is the column
    for (y, x), val in np.ndenumerate(opp_board):
        if val == '':
            ship_alignments = ai_help.alignments_in(y, x, opp_board, opp_ships)
            ai_help.reduce_alignments(y, x, ship_sets, ship_alignments)

            for ship in ship_alignments:
                ship_modifiers[ship] = 1

    # Run each heuristic to modify the scores.
    for heuristic in heuristics:
        heuristic[0](cell_modifiers, ship_modifiers, ship_sets, *heuristics[1])

    # Apply resulting weights.
    for (y, x), val in np.ndenumerate(scores):
        for ship in ship_sets[(y, x)]:
            scores[y, x] += ship_modifiers[ship]
        scores[y, x] *= cell_modifiers[y, x]

    return scores


def ship_adjacency_heuristic(cell_modifiers, ship_modifiers, ship_sets, adj_weight, board):
    adj_cells = get_cells_adjacent_to_ships(board)
    affected_ships = set()
    for cell in adj_cells:
        if cell in ship_sets:
            # joins two sets
            affected_ships |= ship_sets[cell]

    for ship in affected_ships:
        cell_modifiers[ship] *= adj_weight


def get_cells_adjacent_to_ships(board):
    neighbours = set()
    for (y, x), val in np.ndenumerate(board):
        if val == 'H' or val[0] == 'S':
            if y - 1 >= 0 and board[y - 1, x] == '':
                neighbours.add((y - 1, x))
            # Check below
            if y + 1 < len(board) and board[y + 1, x] == '':
                neighbours.add((y + 1, x))
            # Check left
            if x - 1 >= 0 and board[y, x - 1] == '':
                neighbours.add((y, x - 1))
            # Check right
            if x + 1 < len(board[0]) and board[y, x + 1] == '':
                neighbours.add((y, x + 1))

    return neighbours
