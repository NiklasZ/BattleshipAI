import numpy as np

# Applies a heuristic on potential ships that would be adjacent to known ships.
# Depending on adj_weight this will either prioritise adjacent ships or neglect them.
SEARCH_RANGES = {
    'ship_adjacency':[0.,5.]
}

def ship_adjacency(cell_modifiers, ship_modifiers, ship_sets, board, adj_weight):
    adj_cells = get_cells_adjacent_to_ships(board)
    affected_ships = set()
    for cell in adj_cells:
        if cell in ship_sets:
            # joins two sets
            affected_ships |= ship_sets[cell]

    for ship in affected_ships:
        ship_modifiers[ship] *= adj_weight


def get_cells_adjacent_to_ships(board):
    neighbours = set()
    for (y, x), val in np.ndenumerate(board):
        # If the coordinate is either a hit or sunk ship.
        if val == 'H' or (len(val) == 2 and val[0] == 'S'):
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