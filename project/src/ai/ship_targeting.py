import numpy as np


# =============================================================================
# The code below shows a selection of helper functions designed to make the
# time to understand the environment and to get a game running as short as
# possible. The code also serves as an example of how to manipulate the myBoard
# and opp_board dictionaries that are in gameState.

# Gets all possible alignments on a board. The optional parameter allows
# removing redundant alignments.
from src.ai.ship_deployment import can_deploy


def possible_alignments(opp_board, opp_ships, reduce=False):
    alignments = np.zeros((len(opp_board), len(opp_board[0])), dtype=int)
    # A dict of coordinates and their valid ship alignments.
    ship_sets = {}
    # y is the row, x is the column
    for y in range(0, len(opp_board)):
        for x in range(0, len(opp_board[0])):
            if opp_board[y][x] == '':
                ship_alignments = _alignments_in(y, x, opp_board, opp_ships)

                if reduce:
                    _reduce_alignments(y, x, ship_sets, ship_alignments)
                else:
                    ship_sets[(y, x)] = ship_alignments

    for coord, valid_alignments in ship_sets.items():
        alignments[coord] = len(valid_alignments)

    return alignments


# Function that detects and removes redundant alignments if they are complete subsets of another cell.
# In practical terms this means that there is no point at firing at some cell A on a board because there exists another
# cell B that when fired at, can eliminate all possibilities of there being a ship in A.

def _reduce_alignments(y, x, ship_sets, ship_alignments):
    # If is first element, add it and skip checking against itself.
    if len(ship_sets) == 0:
        ship_sets[(y, x)] = ship_alignments
        return

    is_subset = False

    # Compare new alignments to existing ones.
    for coord, valid_alignments in list(ship_sets.items()):
        # If it is a subset of existing alignments, do not add it.
        if ship_alignments.issubset(valid_alignments):
            is_subset = True
            break
        # If an existing element is its subset, remove it.
        elif valid_alignments.issubset(ship_alignments):
            del ship_sets[coord]

    if not is_subset:
        ship_sets[(y, x)] = ship_alignments


# Gets number of valid alignments for a position
# Will return a set of ship deployments each in the form of (y - i, x, ship_length, orientation)
def _alignments_in(y, x, opp_board, opp_ships):
    valid_alignments = set()
    for ship_length in opp_ships:
        for i in range(0, ship_length):
            # Vertical alignment attempts
            if y - i >= 0 and can_deploy(y - i, x, opp_board, ship_length, "V"):
                valid_alignments.add((y - i, x, ship_length, 'V'))
            # Horizontal alignment attempts
            if x - i >= 0 and can_deploy(y, x - i, opp_board, ship_length, "H"):
                valid_alignments.add((y, x - i, ship_length, 'H'))

    return valid_alignments


# Returns whether given location can fit given ship onto given board and, if it can, updates the given board with that ships position


# Returns a list of the lengths of your opponent's ships that haven't been sunk


# Ascertains if a given ship can be deployed at a given location
# The optional valid_fields parameter is for when other types of spaces such as hits (H) should be considered acceptable
# to deploy over.


# Removes a specified ship from a board.


# For a hit option, calculate the number of possible alignments and return the results + possibilities.
def possible_hit_ships(opp_board, opp_ships, position, hit_option):
    # Remove ships that are too short to be possible.
    # possible_ships = np.array(opp_ships) - hit_option['seq_length']
    # possible_ships = possible_ships[possible_ships > 0]
    seq_length = hit_option['seq_length']
    ship_fits = 0

    # Based on the sequence's position, ascertain if there is enough room.
    # This works by trying to deploy a ship in the ranges that include both the sequence and the given position.
    for ship_length in opp_ships:
        if hit_option['direction'] == 'top':
            start_idx = position[0] - (ship_length - seq_length) + 1
            final_idx = position[0]
            for idx in range(start_idx, final_idx + 1):
                if idx >= 0 and can_deploy(idx, position[1], opp_board, ship_length, 'V', valid_fields=['', 'H']):
                    ship_fits += 1

        if hit_option['direction'] == 'bottom':
            start_idx = position[0] - ship_length + 1
            final_idx = position[0] - seq_length
            for idx in range(start_idx, final_idx + 1):
                if idx >= 0 and can_deploy(idx, position[1], opp_board, ship_length, 'V', valid_fields=['', 'H']):
                    ship_fits += 1

        if hit_option['direction'] == 'left':
            start_idx = position[1] - (ship_length - seq_length) + 1
            final_idx = position[1]
            for idx in range(start_idx, final_idx + 1):
                if idx >= 0 and can_deploy(position[0], idx, opp_board, ship_length, 'H', valid_fields=['', 'H']):
                    ship_fits += 1

        if hit_option['direction'] == 'right':
            start_idx = position[1] - ship_length + 1
            final_idx = position[1] - seq_length
            for idx in range(start_idx, final_idx + 1):
                if idx >= 0 and can_deploy(position[0], idx, opp_board, ship_length, 'H', valid_fields=['', 'H']):
                    ship_fits += 1

    return ship_fits


# Find locations adjacent to possible hits and records their lengths.
def adjacent_to_hits(opp_board):
    hits = {}
    vert_visited = np.zeros((len(opp_board), len(opp_board[0])), dtype=bool)
    horz_visited = np.zeros((len(opp_board), len(opp_board[0])), dtype=bool)
    for (y, x), val in np.ndenumerate(opp_board):
        if opp_board[y][x] == 'H':
            # Search vertically
            if not vert_visited[y, x]:
                vert_visited[y, x] = True
                vert_length = 1
                top = bottom = None

                # Search above
                i = 1
                while y - i >= 0:
                    if opp_board[y - i][x] == 'H':
                        vert_visited[y - i, x] = True
                        vert_length += 1
                    else:
                        if opp_board[y - i][x] == '':
                            top = (y - i, x)
                        break
                    i += 1

                # Search below
                i = 1
                while y + i < len(opp_board):
                    if opp_board[y + i][x] == 'H':
                        vert_visited[y + i, x] = True
                        vert_length += 1
                    else:
                        if opp_board[y + i][x] == '':
                            bottom = (y + i, x)
                        break
                    i += 1

                if top:
                    _add_to_hits(hits, top, vert_length, 'top')
                if bottom:
                    _add_to_hits(hits, bottom, vert_length, 'bottom')

            # Search horizontally
            if not horz_visited[y, x]:
                horz_visited[y, x] = True
                horz_length = 1
                left = right = None

                # Search left
                j = 1
                while x - j >= 0:
                    if opp_board[y][x - j] == 'H':
                        horz_length[y, x - j] = True
                        horz_length += 1
                    else:
                        if opp_board[y][x - j] == '':
                            left = (y, x - j)
                        break
                    j += 1

                # Search right
                j = 1
                while x + j < len(opp_board[0]):
                    if opp_board[y][x + j] == 'H':
                        horz_visited[y, x + j] = True
                        horz_length += 1
                    else:
                        if opp_board[y][x + j] == '':
                            right = (y, x + j)
                        break
                    j += 1

                if left:
                    _add_to_hits(hits, left, horz_length, 'left')
                if right:
                    _add_to_hits(hits, right, horz_length, 'right')

    return hits


# Helper method for adding hits. If multiple ship lengths intersect, it will
# prioritise the larger one. This can happen when multiple ships are adjacent
# and the AI runs out of options along one length, but has not sunk any ships, instead having hit several.
def _add_to_hits(hits, coord, seq_length, direction):
    if coord not in hits:
        hits[coord] = {'seq_length': seq_length, 'direction': direction}
    elif seq_length > hits[coord]['seq_length']:
        hits[coord] = {'seq_length': seq_length, 'direction': direction}


# Count the number of hits and misses on a board.


# Deploys all the ships randomly on a blank board


# Detects if there is land on the board


# Given a valid coordinate on the board returns it as a correctly formatted move on a battleship grid.


# Given a formatted move on a battleship, extract the original array indices.


# Given a valid coordinate on the board returns it as a correctly formatted ship

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
            ship_alignments = _alignments_in(y, x, opp_board, opp_ships)
            ship_sets[(y, x)] = ship_alignments
            _reduce_alignments(y, x, reduced_ship_sets, ship_alignments)

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