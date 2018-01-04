# This module contains all functions related to scoring possible targets for a ship. These will be called by a bot
# to receive a recommendation as to where it is best to shoot next.

# project imports
import src.ai.ship_deployment as ship_deploy

# library imports
import numpy as np


def possible_alignments(board, ships, reduce=False):
    """
    Counts how many possible ship alignments there are on each cell on the board. So if for coordinate (0,1), there are
    2 possible ships that can be fit to lie on this coordinate then returned_array[0,1] = 2.
    :param board: a 2D numpy array containing a string representation of the board.
    :param ships: a list of ints, where each int is the length of a ship on the board.
    :param reduce: an optional parameter that will call a function that sets redundant alignments to 0. More details
    in _reduce_alignments.
    :return: a 2D numpy array containing integers, each a count of the possible alignments per cell.
    """
    # board in which to store the alignments.
    alignments = np.zeros((len(board), len(board[0])), dtype=int)
    # A dict of coordinates and their valid ship alignments. Maps as follows {coordinate:set(ship_1,ship_2,ship_3,...)}
    # where each set is a tuple containing the information necessary to uniquely identify a ship.
    ship_sets = {}
    # y is the row, x is the column
    for y in range(0, len(board)):
        for x in range(0, len(board[0])):
            # only bother with empty cells (as it is otherwise always 0).
            if board[y][x] == '':
                # find alignments per cell
                ship_alignments = _alignments_in(y, x, board, ships)

                # Optionally check if the found alignments are redundant.
                if reduce:
                    _reduce_alignments(y, x, ship_sets, ship_alignments)
                else:
                    ship_sets[(y, x)] = ship_alignments

    # Set each coordinate to the number of alignments.
    for coord, valid_alignments in ship_sets.items():
        alignments[coord] = len(valid_alignments)

    return alignments


def _reduce_alignments(y, x, ship_sets, ship_alignments):
    """
    Function that detects and removes a coordinate's alignments if it is a subset of another coordinate's alignments.
    This means for example that if coordinate (y,x) can fit ships s_1, s_2 and there is already some other coordinate C
    in ship_sets that can fit s_1,s_2 and possibly other ships, there is no gain to ever firing at (y,x) as firing at C
    will already ascertain if any of the possible ships are there. Accordingly it in this case removes the alignments of
    (y,x) as they are subset-equal to C's alignments.
    The reverse case where (y,x) has alignments of which the alignments some C in ship_sets in a subset is also
    accounted for. Finally, in order for this to work, we need to assume that the sets in ship_sets are not subsets of
    each other.
    :param y: row index of the coordinate
    :param x: column index of the coordinate
    :param ship_sets: a dictionary that maps a coordinate to a set of ships
     of the form {coordinate:set(ship_1,ship_2,ship_3,...)}
    :param ship_alignments: this is a set of the ships for the coordinate (y,x).
    :return: None
    """
    # If is first element to add to ship_sets, add it and skip checking against itself.
    if len(ship_sets) == 0:
        ship_sets[(y, x)] = ship_alignments
        return

    is_subset = False

    # Compare new alignments to existing ones.
    for coord, valid_alignments in list(ship_sets.items()):
        # If (y,x)'s alignments are a subset of existing alignments, do not add it.
        if ship_alignments.issubset(valid_alignments):
            is_subset = True
            break
        # If an existing element's alignments are subset to (y,x)'s alignments, remove it.
        elif valid_alignments.issubset(ship_alignments):
            del ship_sets[coord]

    # If the (y,x)'s alignments are not subset to any alignments in ship_sets add the alignments.
    if not is_subset:
        ship_sets[(y, x)] = ship_alignments


def _alignments_in(y, x, opp_board, opp_ships):
    """
    Determines which ships can be placed so they intersect with the given (y,x) coordinate.
    :param y:
    :param x:
    :param opp_board:
    :param opp_ships:
    :return: A set of tuples, where each tuple has the form: (y_ship, x_ship, ship_length,
    """
    valid_alignments = set() # Set of tuples, where each tuple is a unique ship.
    for ship_id,ship_length in enumerate(opp_ships):
        # This index shifts the a ship across the coordinate.
        for i in range(0, ship_length):
            # Vertical alignment attempts
            if y - i >= 0 and ship_deploy.can_deploy(y - i, x, opp_board, ship_length, "V"):
                # Add a tuple of the ship to identify it.
                valid_alignments.add((y - i, x, ship_length, 'V',ship_id))
            # Horizontal alignment attempts
            if x - i >= 0 and ship_deploy.can_deploy(y, x - i, opp_board, ship_length, "H"):
                # Add a tuple of the ship to identify it.
                valid_alignments.add((y, x - i, ship_length, 'H',ship_id))

    return valid_alignments


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
                if idx >= 0 and ship_deploy.can_deploy(idx, position[1], opp_board, ship_length, 'V',
                                                       valid_fields=['', 'H']):
                    ship_fits += 1

        if hit_option['direction'] == 'bottom':
            start_idx = position[0] - ship_length + 1
            final_idx = position[0] - seq_length
            for idx in range(start_idx, final_idx + 1):
                if idx >= 0 and ship_deploy.can_deploy(idx, position[1], opp_board, ship_length, 'V',
                                                       valid_fields=['', 'H']):
                    ship_fits += 1

        if hit_option['direction'] == 'left':
            start_idx = position[1] - (ship_length - seq_length) + 1
            final_idx = position[1]
            for idx in range(start_idx, final_idx + 1):
                if idx >= 0 and ship_deploy.can_deploy(position[0], idx, opp_board, ship_length, 'H',
                                                       valid_fields=['', 'H']):
                    ship_fits += 1

        if hit_option['direction'] == 'right':
            start_idx = position[1] - ship_length + 1
            final_idx = position[1] - seq_length
            for idx in range(start_idx, final_idx + 1):
                if idx >= 0 and ship_deploy.can_deploy(position[0], idx, opp_board, ship_length, 'H',
                                                       valid_fields=['', 'H']):
                    ship_fits += 1

    return ship_fits


def possible_hit_scores(opp_board, opp_ships, position, hit_option, heuristics):
    # Remove ships that are too short to be possible.
    seq_length = hit_option['seq_length']
    cell_modifiers = np.ones((len(opp_board), len(opp_board[0])), dtype=float)  # modifiers to apply to cell.
    ship_modifiers = {}  # modifiers to apply to ship.
    # A dict of coordinates and their valid ship alignments. This is useful as some heuristics will need to have
    # full alignment data to make decisions.
    ship_set = set()
    score = 0

    # Based on the sequence's position, ascertain if there is enough room.
    # This works by trying to deploy a ship in the ranges that include both the sequence and the given position.
    for ship_length in opp_ships:
        if hit_option['direction'] == 'top':
            start_idx = position[0] - (ship_length - seq_length) + 1
            final_idx = position[0]
            for idx in range(start_idx, final_idx + 1):
                if idx >= 0 and ship_deploy.can_deploy(idx, position[1], opp_board, ship_length, 'V',
                                                       valid_fields=['', 'H']):
                    ship = (idx, position[1], ship_length, 'V')
                    ship_set.add(ship)
                    ship_modifiers[ship] = 1

        if hit_option['direction'] == 'bottom':
            start_idx = position[0] - ship_length + 1
            final_idx = position[0] - seq_length
            for idx in range(start_idx, final_idx + 1):
                if idx >= 0 and ship_deploy.can_deploy(idx, position[1], opp_board, ship_length, 'V',
                                                       valid_fields=['', 'H']):
                    ship = (idx, position[1], ship_length, 'V')
                    ship_set.add(ship)
                    ship_modifiers[ship] = 1

        if hit_option['direction'] == 'left':
            start_idx = position[1] - (ship_length - seq_length) + 1
            final_idx = position[1]
            for idx in range(start_idx, final_idx + 1):
                if idx >= 0 and ship_deploy.can_deploy(position[0], idx, opp_board, ship_length, 'H',
                                                       valid_fields=['', 'H']):
                    ship = (position[0], idx, ship_length, 'H')
                    ship_set.add(ship)
                    ship_modifiers[ship] = 1

        if hit_option['direction'] == 'right':
            start_idx = position[1] - ship_length + 1
            final_idx = position[1] - seq_length
            for idx in range(start_idx, final_idx + 1):
                if idx >= 0 and ship_deploy.can_deploy(position[0], idx, opp_board, ship_length, 'H',
                                                       valid_fields=['', 'H']):
                    ship = (position[0], idx, ship_length, 'H')
                    ship_set.add(ship)
                    ship_modifiers[ship] = 1

    # Run each heuristic to modify the scores.
    for heuristic in heuristics:
        heuristic[0](cell_modifiers, ship_modifiers, {position: ship_set}, opp_board, heuristic[1])

    # Apply heuristics to position
    for ship in ship_set:
        score += ship_modifiers[ship]
    score *= cell_modifiers[position]

    return score


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
