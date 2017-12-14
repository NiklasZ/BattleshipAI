import numpy as np


# TODO perform subset checks on alignments to remove irrelevant choices entirely (useful when going probabilistic).
# =============================================================================
# The code below shows a selection of helper functions designed to make the
# time to understand the environment and to get a game running as short as
# possible. The code also serves as an example of how to manipulate the myBoard
# and opp_board dictionaries that are in gameState.

def possible_alignments(opp_board, opp_ships):
    alignments = np.zeros((len(opp_board), len(opp_board[0])), dtype=int)
    # y is the row, x is the column
    for y in range(0, len(opp_board)):
        for x in range(0, len(opp_board[0])):
            if opp_board[y][x] == '':
                alignments[y, x] = alignments_in(y, x, opp_board, opp_ships)

    return alignments


# Gets number of valid alignments for a position
def alignments_in(y, x, opp_board, opp_ships):
    valid_alignments = 0
    for shipLength in opp_ships:
        for i in range(0, shipLength):
            # Vertical alignment attempts
            if y - i >= 0 and can_deploy(y - i, x, opp_board, shipLength, "V"):
                valid_alignments += 1
            # Horizontal alignment attempts
            if x - i >= 0 and can_deploy(y, x - i, opp_board, shipLength, "H"):
                valid_alignments += 1

    return valid_alignments


# Deploys all the ships randomly on a blank board
def deploy_randomly(game_state):
    move = []  # Initialise move as an emtpy list
    orientation = None
    row = None
    column = None
    for i in range(len(game_state["Ships"])):  # For every ship that needs to be deployed
        deployed = False
        while not deployed:  # Keep randomly choosing locations until a valid one is chosen
            row = np.random.randint(0, len(game_state["MyBoard"]) - 1)  # Randomly pick a row
            column = np.random.randint(0, len(game_state["MyBoard"][0]) - 1)  # Randomly pick a column
            orientation = np.random.choice(["H", "V"])  # Randomly pick an orientation
            if deploy_ship(row, column, game_state["MyBoard"], game_state["Ships"][i], orientation,
                           i):  # If ship can be successfully deployed to that location...
                deployed = True  # ...then the ship has been deployed
        move.append({"Row": chr(row + 65), "Column": (column + 1),
                     "Orientation": orientation})  # Add the valid deployment location to the list of deployment locations in move
    return {"Placement": move}  # Return the move


# Returns whether given location can fit given ship onto given board and, if it can, updates the given board with that ships position
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


# Returns a list of the lengths of your opponent's ships that haven't been sunk
def ships_still_afloat(game_state):
    afloat = []
    ships_removed = []
    for k in range(len(game_state["Ships"])):  # For every ship
        afloat.append(game_state["Ships"][k])  # Add it to the list of afloat ships
        ships_removed.append(False)  # Set its removed from afloat list to false
    for i in range(len(game_state["OppBoard"])):
        for j in range(len(game_state["OppBoard"][0])):  # For every grid on the board
            for k in range(len(game_state["Ships"])):  # For every ship
                if str(k) in game_state["OppBoard"][i][j] and not ships_removed[
                    k]:  # If we can see the ship number on our opponent's board and we haven't already removed it from the afloat list
                    afloat.remove(game_state["Ships"][
                                      k])  # Remove that ship from the afloat list (we can only see an opponent's ship number when the ship has been sunk)
                    ships_removed[
                        k] = True  # Record that we have now removed this ship so we know not to try and remove it again
    return afloat  # Return the list of ships still afloat


# Ascertains if a given ship can be deployed at a given location
# The optional valid_fields parameter is for when other types of spaces such as hits (H) should be considered acceptable
# to deploy over.
def can_deploy(i, j, board, length, orientation, valid_fields=['']):
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


# Given a valid coordinate on the board returns it as a correctly formatted move
def translate_move(row, column):
    return {"Row": chr(row + 65), "Column": (column + 1)}


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
            for idx in range(start_idx, final_idx+1):
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
                    add_to_hits(hits, top, vert_length, 'top')
                if bottom:
                    add_to_hits(hits, bottom, vert_length, 'bottom')

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
                    add_to_hits(hits, left, horz_length, 'left')
                if right:
                    add_to_hits(hits, right, horz_length, 'right')

    return hits


# Helper method for adding hits. If multiple ship lengths intersect, it will
# prioritise the larger one. Normally this should never happen if the AI greedily
# hunts down the longest found ship before bothering with another one.
def add_to_hits(hits, coord, seq_length, direction):
    if coord not in hits:
        hits[coord] = {'seq_length': seq_length, 'direction': direction}
    elif seq_length > hits[coord]['seq_length']:
        print("Why is this executing?!")
        hits[coord] = {'seq_length': seq_length, 'direction': direction}
