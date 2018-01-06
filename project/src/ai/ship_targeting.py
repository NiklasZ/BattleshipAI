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


def _alignments_in(y, x, board, ships):
    """
    Determines which ships can be placed so they intersect with the given (y,x) coordinate. Then returns a set
     of those ships.
    :param y: row index of the coordinate
    :param x: column index of the coordinate
    :param board: a 2D numpy array containing a string representation of the board.
    :param ships: a list of ints, where each int is the length of a ship on the board.
    :return: A set of tuples, where each tuple has the form: (y_ship, x_ship, ship_length, ship_id)
    """
    valid_alignments = set()  # Set of tuples, where each tuple is a unique ship.
    for ship_id, ship_length in enumerate(ships):
        # This index shifts the a ship across the coordinate.
        for i in range(0, ship_length):
            # Vertical alignment attempts
            if y - i >= 0 and ship_deploy.can_deploy(y - i, x, board, ship_length, "V"):
                # Add a tuple of the ship to identify it.
                valid_alignments.add((y - i, x, ship_length, 'V', ship_id))
            # Horizontal alignment attempts
            if x - i >= 0 and ship_deploy.can_deploy(y, x - i, board, ship_length, "H"):
                # Add a tuple of the ship to identify it.
                valid_alignments.add((y, x - i, ship_length, 'H', ship_id))

    return valid_alignments


def possible_hit_ships(board, ships, coordinate, hit_option):
    """
    This function counts the number of ships that could be in a coordinate, given the presence of a sequence of hits
    next to it. It generally assumes that a hit sequence is of only 1 ship as opposed to several adjacent ships.
    :param board: a 2D numpy array containing a string representation of the board.
    :param ships: a list of ints, where each int is the length of a ship on the board.
    :param coordinate: the chosen position adjacent to the hit sequence.
    :param hit_option: a dictionary that denotes a sequence of hits on the board. It has the form:
    {'seq_length': length of sequence, 'direction': where the coordinate is relative to the sequence}.
    :return: a count of ships that fit in this adjacent coordinate, given the hit sequence, board and ships.
    """
    seq_length = hit_option['seq_length']  # length of sequence of hits.
    ship_fits = 0  # count of ships that could be this sequence.
    y, x = coordinate

    # Based on the sequence's position, ascertain if there is enough room to fit a ship length.
    # This works by trying to deploy a ship in the ranges that include both the sequence and the given position.
    for ship_length in ships:
        # If the coordinate is above the hit sequence.
        if hit_option['direction'] == 'top':
            start_idx = y - (ship_length - seq_length) + 1  # Highest possible position that includes the sequence.
            final_idx = y  # Position that includes the coordinate.
            # iterates through each position and checks deployment if the index is valid.
            for idx in range(start_idx, final_idx + 1):
                if idx >= 0 and ship_deploy.can_deploy(idx, x, board, ship_length, 'V',
                                                       valid_fields=['', 'H']):
                    ship_fits += 1

        # If the coordinate is below the hit sequence.
        if hit_option['direction'] == 'bottom':
            start_idx = y - ship_length + 1  # Highest possible position that includes the coordinate
            final_idx = y - seq_length  # Highest possible position that includes the sequence.
            for idx in range(start_idx, final_idx + 1):
                if idx >= 0 and ship_deploy.can_deploy(idx, x, board, ship_length, 'V',
                                                       valid_fields=['', 'H']):
                    ship_fits += 1

        # If the coordinate is to the left of hit sequence.
        if hit_option['direction'] == 'left':
            start_idx = x - (ship_length - seq_length) + 1
            final_idx = x
            for idx in range(start_idx, final_idx + 1):
                if idx >= 0 and ship_deploy.can_deploy(y, idx, board, ship_length, 'H',
                                                       valid_fields=['', 'H']):
                    ship_fits += 1

        # If the coordinate is to the right of the hit sequence.
        if hit_option['direction'] == 'right':
            start_idx = x - ship_length + 1
            final_idx = x - seq_length
            for idx in range(start_idx, final_idx + 1):
                if idx >= 0 and ship_deploy.can_deploy(y, idx, board, ship_length, 'H',
                                                       valid_fields=['', 'H']):
                    ship_fits += 1

    return ship_fits


def possible_hit_scores(board, ships, coordinate, hit_option, heuristics):
    """
    A variant of possible_hit_ships(), that also allows applying heuristics to give ships and coordinates scores.
    :param board: a 2D numpy array containing a string representation of the board.
    :param ships: a list of ints, where each int is the length of a ship on the board.
    :param coordinate: the chosen position adjacent to the hit sequence.
    :param hit_option: a dictionary that denotes a sequence of hits on the board. It has the form:
    {'seq_length': length of sequence, 'direction': where the coordinate is relative to the sequence}.
    :param heuristics: a list of tuples, where each tuple is (reference to heuristic function, weight)
    :return: a float, denoting the score of the coordinate.
    """
    seq_length = hit_option['seq_length']
    cell_modifiers = np.ones((len(board), len(board[0])), dtype=float)  # modifiers to apply to each coordinate.
    ship_modifiers = {}  # modifiers to apply to ship.
    # A dict of coordinates and their valid ship alignments. This is useful as some heuristics will need to have
    # full alignment data to make decisions.
    ship_set = set()
    score = 0
    y, x = coordinate

    # Based on the sequence's position, ascertain if there is enough room.
    # This works by trying to deploy a ship in the ranges that include both the sequence and the given position.
    for ship_length in ships:
        if hit_option['direction'] == 'top':
            start_idx = y - (ship_length - seq_length) + 1
            final_idx = y
            for idx in range(start_idx, final_idx + 1):
                if idx >= 0 and ship_deploy.can_deploy(idx, x, board, ship_length, 'V',
                                                       valid_fields=['', 'H']):
                    ship = (idx, x, ship_length, 'V')
                    ship_set.add(ship)
                    ship_modifiers[ship] = 1

        if hit_option['direction'] == 'bottom':
            start_idx = y - ship_length + 1
            final_idx = y - seq_length
            for idx in range(start_idx, final_idx + 1):
                if idx >= 0 and ship_deploy.can_deploy(idx, x, board, ship_length, 'V',
                                                       valid_fields=['', 'H']):
                    ship = (idx, x, ship_length, 'V')
                    ship_set.add(ship)
                    ship_modifiers[ship] = 1

        if hit_option['direction'] == 'left':
            start_idx = x - (ship_length - seq_length) + 1
            final_idx = x
            for idx in range(start_idx, final_idx + 1):
                if idx >= 0 and ship_deploy.can_deploy(y, idx, board, ship_length, 'H',
                                                       valid_fields=['', 'H']):
                    ship = (y, idx, ship_length, 'H')
                    ship_set.add(ship)
                    ship_modifiers[ship] = 1

        if hit_option['direction'] == 'right':
            start_idx = x - ship_length + 1
            final_idx = x - seq_length
            for idx in range(start_idx, final_idx + 1):
                if idx >= 0 and ship_deploy.can_deploy(y, idx, board, ship_length, 'H',
                                                       valid_fields=['', 'H']):
                    ship = (y, idx, ship_length, 'H')
                    ship_set.add(ship)
                    ship_modifiers[ship] = 1

    # Run each heuristic to modify the scores.
    for heuristic in heuristics:
        heuristic[0](cell_modifiers, ship_modifiers, {coordinate: ship_set}, board, heuristic[1])

    # Apply heuristics to position
    for ship in ship_set:
        score += ship_modifiers[ship]
    score *= cell_modifiers[coordinate]

    return score


def adjacent_to_hits(board):
    """
    This function gets all coordinates adjacent to a sequence of hits of any length. It maps each coordinate to the
    longest sequence it is adjacent to. So if there is a HHH sequence to the left and a HH sequence above
    some coordinate C, then C will be mapped to the sequence to th left of it.
    :param board: a 2D numpy array containing a string representation of the board.
    :return: a dictionary of coordinates adjacent to hits, with the following structure:
    {coordinate:{'seq_length': length of sequence, 'direction': where the coordinate is relative to the sequence},...}
    """
    adjacent_to_hits = {}
    # These arrays denote when a sequence of hits has already been visited vertically or horizontally. Keeping track
    # of these avoids double-counting.
    vert_visited = np.zeros((len(board), len(board[0])), dtype=bool)
    horz_visited = np.zeros((len(board), len(board[0])), dtype=bool)
    # Check each coordinate
    for (y, x), val in np.ndenumerate(board):
        # Only consider a coordinate if it is a hit.
        if val == 'H':
            # Ensure sequence has not been visited vertically.
            if not vert_visited[y, x]:
                vert_visited[y, x] = True
                vert_length = 1  # length of a sequence
                top = bottom = None  # potential adjacent coordinates.

                # Travel up hit sequence to find first empty coordinate above.
                i = 1
                # keep traversing upwards as long as there are hits and we are not at the edge of the board.
                while y - i >= 0:
                    if board[y - i][x] == 'H':
                        vert_visited[y - i, x] = True
                        vert_length += 1
                    # if we encounter an empty coordinate note this position.
                    else:
                        if board[y - i][x] == '':
                            top = (y - i, x)
                        break
                    i += 1

                    # Travel down hit sequence to find first empty coordinate below.
                i = 1
                while y + i < len(board):
                    if board[y + i][x] == 'H':
                        vert_visited[y + i, x] = True
                        vert_length += 1
                    # if we encounter an empty coordinate note this position.
                    else:
                        if board[y + i][x] == '':
                            bottom = (y + i, x)
                        break
                    i += 1

                # If we find an empty coordinate above or below, add to the adjacency dict.
                if top:
                    _add_to_hits(adjacent_to_hits, top, vert_length, 'top')
                if bottom:
                    _add_to_hits(adjacent_to_hits, bottom, vert_length, 'bottom')

            # Same pattern as above, but horizontal.
            if not horz_visited[y, x]:
                horz_visited[y, x] = True
                horz_length = 1
                left = right = None

                # Search left
                j = 1
                while x - j >= 0:
                    if board[y][x - j] == 'H':
                        horz_length[y, x - j] = True
                        horz_length += 1
                    else:
                        if board[y][x - j] == '':
                            left = (y, x - j)
                        break
                    j += 1

                # Search right
                j = 1
                while x + j < len(board[0]):
                    if board[y][x + j] == 'H':
                        horz_visited[y, x + j] = True
                        horz_length += 1
                    else:
                        if board[y][x + j] == '':
                            right = (y, x + j)
                        break
                    j += 1

                if left:
                    _add_to_hits(adjacent_to_hits, left, horz_length, 'left')
                if right:
                    _add_to_hits(adjacent_to_hits, right, horz_length, 'right')

    return adjacent_to_hits


def _add_to_hits(adjacent_to_hits, coord, seq_length, direction):
    """
    This is a helper method for adjacent_to_hits(). It takes the current dictionary of coordinates adjacent to hits and
    will either map the found sequence to a coordinate or, if there is an existing one, compare them and keep the longer
    one.
    :param adjacent_to_hits: a dictionary of coordinates adjacent to hits, with the following structure:
    {coordinate:{'seq_length': length of sequence, 'direction': where the coordinate is relative to the sequence},...}
    :param coord: the discovered position adjacent to the hit sequence.
    :param seq_length: the length of hit sequence
    :param direction: a string representing the direction in which the coordinate is relative to the hit sequence.
    :return: None
    """
    if coord not in adjacent_to_hits:
        adjacent_to_hits[coord] = {'seq_length': seq_length, 'direction': direction}
    elif seq_length > adjacent_to_hits[coord]['seq_length']:
        adjacent_to_hits[coord] = {'seq_length': seq_length, 'direction': direction}


def targeting_scores(board, ships, heuristics):
    """
    A variant of possible_alignments() that incorporates heuristics. It takes the basic alignments for each coordinate
    and then passes it to the provided heuristic functions together with two structures that contain weights. The first
    is cell_modifiers which holds a grid of ones, which act as coordinate weights. The 2nd is ship_modifiers which holds
    a dictionary of ships, where each discovered ship maps to a weight (initially 1). Heuristics can then make changes
    to these before they're used to compute the final score.
    Each ship's weight is added to the cell in which it is present and each cell itself is afterwards multiplied by its
    weight in cell_modifiers. This then yields the score per cell.
    :param board: a 2D numpy array containing a string representation of the board.
    :param ships: a list of ints, where each int is the length of a ship on the board.
    :param heuristics: a list of tuples, where each tuple is (reference to heuristic function, weight)
    :return: a 2D numpy array containing floats, each a score per cell.
    """
    scores = np.zeros((len(board), len(board[0])), dtype=float)  # final scores
    # Modifiers for heuristics to use.
    cell_modifiers = np.ones((len(board), len(board[0])), dtype=float)  # modifiers to apply to cell.
    ship_modifiers = {}  # modifiers to apply to ship.
    # A dict of coordinates and their valid ship alignments. This is useful as some heuristics will need to have
    # full alignment data to make decisions.
    ship_sets = {}
    # A dict of non-redundant coordinates and valid ship alignments. Useful to avoid weighting pointless positions.
    reduced_ship_sets = {}
    # y is the row, x is the column
    for (y, x), val in np.ndenumerate(board):
        if val == '':
            ship_alignments = _alignments_in(y, x, board, ships)
            ship_sets[(y, x)] = ship_alignments
            # Reduce redundant alignments.
            _reduce_alignments(y, x, reduced_ship_sets, ship_alignments)

            for ship in ship_alignments:
                ship_modifiers[ship] = 1

    # Run each heuristic to modify the scores.
    for heuristic in heuristics:
        heuristic[0](cell_modifiers, ship_modifiers, ship_sets, board, heuristic[1])

    # Apply resulting weights.
    for (y, x), val in np.ndenumerate(scores):
        # Account for non-available coordinates.
        if (y, x) in reduced_ship_sets:
            for ship in reduced_ship_sets[(y, x)]:
                scores[y, x] += ship_modifiers[ship]
            scores[y, x] *= cell_modifiers[y, x]

    return scores
