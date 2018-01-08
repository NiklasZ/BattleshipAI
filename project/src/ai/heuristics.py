# This module holds heuristics and their sub-functions. A heuristic generally has a predefined form, taking in
# cell_modifiers, ship_modifiers, ship_sets, board and some weight to optimise.

# Library imports
import numpy as np

# Search are bounds that are considered for optimising the heuristic. It is not advisable to include 0 in this as it can
# result in a score being multiplied with 0 and a coordinate of this score never being fired at.
SEARCH_RANGES = {
    'ship_adjacency': [0.05, 5.]
}


def ship_adjacency(cell_modifiers, ship_modifiers, ship_sets, board, adj_weight):
    """
    Calculates which possible deployable ships are adjacent to known ships. It then multiplies each of these ships'
    score with a weight.
    :param cell_modifiers: a grid of weights to modify
    :param ship_modifiers: a list of possible ships, each with a weight to modify.
    :param ship_sets: the possible ships, mapped by coordinate in which they appear.
    :param board: the board of ships whose neighbourhood should be detected.
    :param adj_weight: a multiplicative weight for an optimisation algorithm to adjust.
    :return:
    """
    adj_cells = _get_cells_adjacent_to_ships(board)
    affected_ships = set()
    for cell in adj_cells:
        if cell in ship_sets:
            # joins two sets
            affected_ships |= ship_sets[cell]

    for ship in affected_ships:
        ship_modifiers[ship] *= adj_weight

    return


def _get_cells_adjacent_to_ships(board):
    """
    Obtains all empty cells next to sunken ships.
    :param board: the board of ships.
    :return: a set of coordinates, each being a neighbour.
    """
    neighbours = set()
    for (y, x), val in np.ndenumerate(board):
        # If the coordinate is either a hit or sunk ship.
        if len(val) == 2 and val[0] == 'S':
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
