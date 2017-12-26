from random import shuffle

import numpy as np

import src.ai

def randomly_space_ships(player_board, ships):
    available_coords = []
    placements = []
    attempts = 0
    # Find all available coordinates.
    for (y, x), val in np.ndenumerate(player_board):
        if val == '':
            available_coords.append((y, x))

    shuffle(available_coords)
    available_coords = set(available_coords)

    # Search for a placement that spaces out the ships as as desired.
    if _place_spaced_ship(available_coords, player_board, ships, placements, attempts):
        return placements

    # In case there is no way to place the ships to be completely non-adjacent.
    return None


def _place_spaced_ship(available_coords, board, ships, placements, attempts):
    # If all ships have been placed, return.
    if len(ships) == 0:
        return True

    # Take a ship from the list and try to fit it.
    ship = ships.pop()
    ship_no = len(ships)

    # Go through each possible coordinate and alignment.
    shuffled_coords = list(available_coords)
    shuffle(shuffled_coords)

    for coord in shuffled_coords:
        y, x = coord

        # The directions are shuffled to avoid predictable alignments whenever it is easy to place ships.
        orientation = ['V', 'H']
        shuffle(orientation)
        for o in orientation:
            # Try to deploy the ship
            result = _deploy_ship_via_coords(coord, board, ship, o, ship_no, available_coords)
            attempts += 1
            if result:
                # If successful, append the positioning (avoids having to search for it later).
                placements.append(
                    {'position': coord, 'ship': ship, 'ship_no': ship_no, 'orientation': o, 'attempts': attempts})
                # Copy the available coordinates and remove the used ones.
                new_available_coords = set(available_coords)
                _remove_neighbouring_coords(coord, o, new_available_coords, ship, board)
                # Recurse and try the next ship.
                if _place_spaced_ship(new_available_coords, board, ships, placements, attempts):
                    return True
                # If this proves unsuccessful, remove this ship placement and try again.
                else:
                    placements.pop()
                    remove_ship(y, x, board, ship, o)

    # Re-attach the ship as the search was unsuccessful.
    ships.append(ship)

    # Not all ships have been placed and the permutations in this part are exhausted.
    return False


def _remove_neighbouring_coords(position, orientation, available_coords, ship, board):
    y, x = position

    if orientation == 'V':
        for i in range(y, y + ship):
            _remove_neighbours((i, x), available_coords, board)
    if orientation == 'H':
        for j in range(x, x + ship):
            _remove_neighbours((y, j), available_coords, board)


def _remove_neighbours(coordinate, available_coords, board):
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


def _deploy_ship_via_coords(coordinate, board, length, orientation, ship_num, available_coordinates):
    y, x = coordinate
    if orientation == "V":  # If we are trying to place ship vertically
        if y + length - 1 >= len(board):  # If ship doesn't fit within board boundaries
            return False  # Ship not deployed
        for i in range(length):  # For every section of the ship
            if (y + i, x) not in available_coordinates:  # If there is something on the board obstructing the ship
                return False  # Ship not deployed
        for i in range(length):  # For every section of the ship
            board[y + i][x] = str(ship_num)  # Place the ship on the board
    else:  # If we are trying to place ship horizontally
        if x + length - 1 >= len(board[0]):  # If ship doesn't fit within board boundaries
            return False  # Ship not deployed
        for j in range(length):  # For every section of the ship
            if (y, x + j) not in available_coordinates:  # If there is something on the board obstructing the ship
                return False  # Ship not deployed
        for j in range(length):  # For every section of the ship
            board[y][x + j] = str(ship_num)  # Place the ship on the board
    return True  # Ship deployed


def deploy_randomly(ships, board):
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
            if _deploy_ship_via_coords(row, column, board, ships[i], orientation,
                                       i):  # If ship can be successfully deployed to that location...
                deployed = True  # ...then the ship has been deployed
        move.append({"Row": chr(row + 65), "Column": (column + 1),
                     "Orientation": orientation})  # Add the valid deployment location to the list of deployment locations in move
    return {"Placement": move}  # Return the move


def translate_ship(row, column, orientation):
    return {"Row": chr(row + 65), "Column": (column + 1), "Orientation": orientation}


def format_ship_deployment(placements):
    accepted_format = []
    ordered = sorted(placements, key=lambda x: x['ship_no'])
    for entry in ordered:
        y, x = entry['position']
        accepted_format.append(translate_ship(y, x, entry['orientation']))

    accepted_format = {"Placement": accepted_format}
    return accepted_format


def deploy_ship(i, j, board, length, orientation, ship_num):
    if orientation == "V":  # If we are trying to place ship vertically
        if i + length - 1 >= len(board):  # If ship doesn't fit within board boundaries
            return False  # Ship not deployed
        for l in range(length):  # For every section of the ship
            if board[i + l][j] != "":  # If there is something on the board obstructing the ship
                return False  # Ship not deployed
        for l in range(length):  # For every section of the ship
            board[i + l][j] = str(ship_num)  # Place the ship on the board
    else:  # If we are trying to place ship horizontally
        if j + length - 1 >= len(board[0]):  # If ship doesn't fit within board boundaries
            return False  # Ship not deployed
        for l in range(length):  # For every section of the ship
            if board[i][j + l] != "":  # If there is something on the board obstructing the ship
                return False  # Ship not deployed
        for l in range(length):  # For every section of the ship
            board[i][j + l] = str(ship_num)  # Place the ship on the board
    return True  # Ship deployed


def can_deploy(i, j, board, length, orientation, valid_fields=None):
    if not valid_fields:
        valid_fields = ['']

    if orientation == "V":  # If we are trying to place ship vertically
        if i + length - 1 >= len(board):  # If ship doesn't fit within board boundaries
            return False  # Ship not deployed
        for l in range(length):  # For every section of the ship
            if board[i + l][j] not in valid_fields:  # If there is something on the board obstructing the ship
                return False  # Ship not deployed
    else:  # If we are trying to place ship horizontally
        if j + length - 1 >= len(board[0]):  # If ship doesn't fit within board boundaries
            return False  # Ship not deployed
        for l in range(length):  # For every section of the ship
            if board[i][j + l] not in valid_fields:  # If there is something on the board obstructing the ship
                return False  # Ship not deployed
    return True  # Ship fits


def remove_ship(y, x, board, ship, orientation):
    if orientation == 'V':
        for i in range(y, y + ship):
            board[i][x] = ''
    else:
        for j in range(x, x + ship):
            board[y][j] = ''
