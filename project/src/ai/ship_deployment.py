# This module holds functions that perform ship placement and removal. These are particularly relevant to defensive
# ship placements.

# Library imports
from random import shuffle
import numpy as np

def randomly_space_ships(board, ships):
    """
    This a top-level function that initiates a search to place ships randomly, with the requirement that none of them
    are horizontally or vertically adjacent (diagonally is permitted). It works by identifying empty coordinates and
    then calling a recursive function _place_spaced_ship() that will attempt to place a ship during each recursive step.
    It is designed to try every possible arrangement of ships in a random order until it finds one that fits.
    :param board: a 2D numpy array containing a string representation of the board.
    :param ships: a list of ints, where each int is the length of a ship on the board.
    :return: a list of ship placements, where each placement is a dictionary of the following structure:
    {'position': starting coordinate, 'ship': ship, 'ship_no': ship index, 'orientation': either vertical or horizontal}
    """
    available_coords = [] # empty coordinates to try and place a ship into.
    placements = [] # list of ship placements
    # Find all available coordinates.
    for (y, x), val in np.ndenumerate(board):
        if val == '':
            available_coords.append((y, x))

    # Shuffle them in place to affect their initial iteration order.
    shuffle(available_coords)
    available_coords = set(available_coords)

    # Search for a placement that spaces out the ships as as desired.
    if _place_spaced_ship(available_coords, board, ships, placements):
        return placements

    # In case there is no way to place the ships to be completely non-adjacent.
    return None


def _place_spaced_ship(available_coords, board, ships, placements):
    """
    Recursive step function that tries to place a ship during each step. It works by taking the set of available
    coordinates and trying each coordinate. During the kth recursive instance it goes through all the available
    coordinates and tries to place it a ship. If successful, it steps into the k+1th instance and continues on with the
    k+1th ship. If it manages to place all ships, it returns True and resolves each previous instance. If a recursive
    instance runs out of possibilities, it returns False and the previous instance has to try placing its ship
    somewhere else. Eventually this way, every possible placement will be tried.
    :param available_coords: a set of coordinates that an instance can try to place a ship on.
    :param board: a 2D numpy array containing a string representation of the board.
    :param ships: a list of ints, where each int is the length of a ship on the board.
    :param placements: a list of ship placements, where each placement is a dictionary of the following structure:
    {'position': starting coordinate, 'ship': ship, 'ship_no': ship index, 'orientation': either vertical or horizontal}
    :return: True, if there are no more ships to place. False, if it is not possible to place the current ship.
    """

    # If all ships have been placed, return.
    if len(ships) == 0:
        return True

    # Take a ship from the list.
    ship = ships.pop()
    ship_no = len(ships)

    # Make a shallow copy of the available coordinates and shuffle them.
    shuffled_coords = list(available_coords)
    shuffle(shuffled_coords)

    # Go through each possible coordinate.
    for coord in shuffled_coords:
        y, x = coord

        # The directions are shuffled to avoid predictable alignments whenever it is easy to place ships.
        orientation = ['V', 'H']
        shuffle(orientation)

        for o in orientation:
            # Try to deploy the ship
            result = _deploy_ship_via_coords(coord, board, ship, o, ship_no, available_coords)
            if result:
                # If successful, append the positioning (avoids having to search for it later).
                placements.append(
                    {'position': coord, 'ship': ship, 'ship_no': ship_no, 'orientation': o})

                # Copy the available coordinates.
                new_available_coords = set(available_coords)
                # Remove the coordinates the ship is on and all its neighbours.
                _remove_current_and_neighbouring_coords(coord, o, new_available_coords, ship, board)
                # Recurse and try the next ship.
                if _place_spaced_ship(new_available_coords, board, ships, placements):
                    return True

                # If we cannot place the next ships, remove this one and try again.
                else:
                    placements.pop()
                    remove_ship(y, x, board, ship, o)

    # Re-attach the popped ship as the search was unsuccessful.
    ships.append(ship)

    # Not all ships have been placed and the permutations in this part are exhausted.
    return False


def _remove_current_and_neighbouring_coords(position, orientation, available_coords, ship_length, board):
    """
    This function removes all coordinates and neighbours of a newly placed ship from available_coords.
    :param position: a coordinate of the starting position of a ship.
    :param orientation: the way the ship is oriented.
    :param available_coords: set of available coordinates for placement to be modified.
    :param ship_length: length of the ship.
    :param board: a 2D numpy array containing a string representation of the board.
    :return:
    """
    y, x = position

    # Choose orientation
    if orientation == 'V':
        # Go through all positions the ship is in.
        for i in range(y, y + ship_length):
            _remove_self_and_neighbours((i, x), available_coords, board)
    if orientation == 'H':
        for j in range(x, x + ship_length):
            _remove_self_and_neighbours((y, j), available_coords, board)


def _remove_self_and_neighbours(coordinate, available_coords, board):
    """
    This function removes a coordinate and its immediate neighbours from available_coords. For each removal, it checks
    whether the coordinate is within the board's bounds and whether it is still in available_coords. The latter is
    necessary as other calls of this function can overlap and remove them beforehand.
    :param coordinate: the chosen coordinate.
    :param available_coords: set of available coordinates for placement to be modified.
    :param board: a 2D numpy array containing a string representation of the board.
    :return:
    """
    y, x = coordinate

    # Remove current position
    if (y, x) in available_coords:
        available_coords.remove((y, x))
    # Check above
    if y - 1 >= 0 and (y - 1, x) in available_coords:
        available_coords.remove((y - 1, x))
    # Check below
    if y + 1 < len(board) and (y + 1, x) in available_coords:
        available_coords.remove((y + 1, x))
    # Check left
    if x - 1 >= 0 and (y, x - 1) in available_coords:
        available_coords.remove((y, x - 1))
    # Check right
    if x + 1 < len(board[0]) and (y, x + 1) in available_coords:
        available_coords.remove((y, x + 1))


def _deploy_ship_via_coords(coordinate, board, ship_length, orientation, ship_num, available_coordinates):
    """
    Deploy a ship at the given coordinate on the board. Checks as to whether it can be placed are done against
    available_coordinates.
    :param coordinate: a coordinate of the starting position of a ship.
    :param board: a 2D numpy array containing a string representation of the board.
    :param ship_length: length of the ship.
    :param orientation: the way the ship is oriented.
    :param ship_num: id or index of the ship.
    :param available_coordinates: a set of coordinates available for placing the ship on.
    :return: True, if the placement was successful. False, if it was not.
    """
    y, x = coordinate
    if orientation == "V":  # If we are trying to place ship vertically
        if y + ship_length - 1 >= len(board):  # If ship doesn't fit within board boundaries
            return False  # Ship not deployed
        for i in range(ship_length):  # For every section of the ship
            if (y + i, x) not in available_coordinates:  # If there is something on the board obstructing the ship
                return False  # Ship not deployed
        for i in range(ship_length):  # For every section of the ship
            board[y + i][x] = str(ship_num)  # Place the ship on the board
    else:  # If we are trying to place ship horizontally
        if x + ship_length - 1 >= len(board[0]):  # If ship doesn't fit within board boundaries
            return False  # Ship not deployed
        for j in range(ship_length):  # For every section of the ship
            if (y, x + j) not in available_coordinates:  # If there is something on the board obstructing the ship
                return False  # Ship not deployed
        for j in range(ship_length):  # For every section of the ship
            board[y][x + j] = str(ship_num)  # Place the ship on the board
    return True  # Ship deployed


def deploy_randomly(ships, board):
    """
    This is a built-in method provided by AIGaming. It randomly places ships until they fit on the board. It then
    formats and returns it.
    :param ships: a list of ship lengths to place.
    :param board: a 2D array containing a string representation of the board.
    :return: a dictionary of these placements in the form:
    {"Placement":[{"Row": ship's row,"Column": ship's column,"Orientation": ship's orientation},...]}
    """
    move = []  # Initialise move as an emtpy list
    orientation = None
    row = None
    column = None
    for i in range(len(ships)):  # For every ship that needs to be deployed
        deployed = False
        while not deployed:  # Keep randomly choosing locations until a valid one is chosen
            row = np.random.randint(0, len(board) - 1)  # Randomly pick a row
            column = np.random.randint(0, len(board[0]) - 1)  # Randomly pick a column
            orientation = np.random.choice(["H", "V"])  # Randomly pick an orientation
            if deploy_ship(row, column, board, ships[i], orientation,
                                       i):  # If ship can be successfully deployed to that location...
                deployed = True  # ...then the ship has been deployed
        move.append({"Row": chr(row + 65), "Column": (column + 1),
                     "Orientation": orientation})  # Add the valid deployment location to the list of deployment locations in move
    return {"Placement": move}  # Return the move


def translate_ship(row, column, orientation):
    """
    This is a built-in method provided by AIGaming. It translates a ship placement of just indices and orientation into
    a battleship-friendly format. The row becomes alphabetical (0=>A,1=>B,etc) and the column indexes at
    1 (0=>1, 1=>2, etc). The orientation stays the same.
    :param row: an integer, making up the row index.
    :param column: an integer, making up the column index.
    :param orientation: the orientation of the ship
    :return: A dictionary in the battleship-friendly format. E.g:
    {"Row": "B","Column": 3,"Orientation": "H"}
    """
    return {"Row": chr(row + 65), "Column": (column + 1), "Orientation": orientation}


def format_ship_deployment(placements):
    """
    Formats the placements from randomly_space_ships() to be battleship-friendly.
    :param placements:  a list of ship placements, where each placement is a dictionary of the following structure:
    {'position': starting coordinate, 'ship': ship, 'ship_no': ship index, 'orientation': either vertical or horizontal}
    :return: a dictionary of these placements in the form:
    {"Placement":[{"Row": ship's row,"Column": ship's column,"Orientation": ship's orientation},...]}
    """
    accepted_format = []
    # Order ships by ship number to ensure they are iterated in the right order.
    ordered = sorted(placements, key=lambda x: x['ship_no'])
    for entry in ordered:
        y, x = entry['position']
        accepted_format.append(translate_ship(y, x, entry['orientation']))

    accepted_format = {"Placement": accepted_format}
    return accepted_format


def deploy_ship(y, x, board, ship_length, orientation, ship_num):
    """
    This is a built-in method provided by AIGaming. Deploys a ship at the given coordinate on the board. Checks as to
    whether it can be placed are done against the board.
    :param y: an integer, making up the row index.
    :param x: an integer, making up the column index.
    :param board: a 2D array containing a string representation of the board.
    :param ship_length: length of the ship.
    :param orientation: the way the ship is oriented.
    :param ship_num: id or index of the ship.
    :return: True, if the placement was successful. False, if it was not.
    """
    if orientation == "V":  # If we are trying to place ship vertically
        if y + ship_length - 1 >= len(board):  # If ship doesn't fit within board boundaries
            return False  # Ship not deployed
        for l in range(ship_length):  # For every section of the ship
            if board[y + l][x] != "":  # If there is something on the board obstructing the ship
                return False  # Ship not deployed
        for l in range(ship_length):  # For every section of the ship
            board[y + l][x] = str(ship_num)  # Place the ship on the board
    else:  # If we are trying to place ship horizontally
        if x + ship_length - 1 >= len(board[0]):  # If ship doesn't fit within board boundaries
            return False  # Ship not deployed
        for l in range(ship_length):  # For every section of the ship
            if board[y][x + l] != "":  # If there is something on the board obstructing the ship
                return False  # Ship not deployed
        for l in range(ship_length):  # For every section of the ship
            board[y][x + l] = str(ship_num)  # Place the ship on the board
    return True  # Ship deployed


def can_deploy(y, x, board, ship_length, orientation, valid_fields=None):
    """
    This function is a slight variant of deploy_ship() and merely checks whether a ship can be deployed somewhere and
    does not actually place it on the board.
    :param y: an integer, making up the row index.
    :param x: an integer, making up the column index.
    :param board: a 2D numpy array containing a string representation of the board.
    :param ship_length: length of the ship.
    :param orientation: the way the ship is oriented.
    :param valid_fields: a list of what fields are considered valid to place a ship over. This option gives it more
    uses.
    :return: True, if the ship can be placement. False, if it was not.
    """
    if not valid_fields:
        valid_fields = ['']

    if orientation == "V":  # If we are trying to place ship vertically
        if y + ship_length - 1 >= len(board):  # If ship doesn't fit within board boundaries
            return False  # Ship not deployed
        for l in range(ship_length):  # For every section of the ship
            if board[y + l][x] not in valid_fields:  # If there is something on the board obstructing the ship
                return False  # Ship not deployed
    else:  # If we are trying to place ship horizontally
        if x + ship_length - 1 >= len(board[0]):  # If ship doesn't fit within board boundaries
            return False  # Ship not deployed
        for l in range(ship_length):  # For every section of the ship
            if board[y][x + l] not in valid_fields:  # If there is something on the board obstructing the ship
                return False  # Ship not deployed
    return True  # Ship fits


def remove_ship(y, x, board, ship, orientation):
    """
    Removes a ship from a given board.
    :param y: starting row of the ship.
    :param x: starting column of the ship.
    :param board: a 2D numpy array containing a string representation of the board.
    :param ship: length of the ship.
    :param orientation: the way the ship is oriented.
    :return:
    """
    if orientation == 'V':
        for i in range(y, y + ship):
            board[i][x] = ''
    else:
        for j in range(x, x + ship):
            board[y][j] = ''
