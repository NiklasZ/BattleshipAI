import numpy as np


def ships_still_afloat(ships, opp_board):
    afloat = []
    ships_removed = []
    for k in range(len(ships)):  # For every ship
        afloat.append(ships[k])  # Add it to the list of afloat shipsA
        ships_removed.append(False)  # Set its removed from afloat list to false
    for i in range(len(opp_board)):
        for j in range(len(opp_board[0])):  # For every grid on the board
            for k in range(len(ships)):  # For every ship
                if str(k) in opp_board[i][j] and not ships_removed[
                    k]:  # If we can see the ship number on our opponent's board and we haven't already removed it from the afloat list
                    afloat.remove(ships[
                                      k])  # Remove that ship from the afloat list (we can only see an opponent's ship number when the ship has been sunk)
                    ships_removed[
                        k] = True  # Record that we have now removed this ship so we know not to try and remove it again
    return afloat  # Return the list of ships still afloat


def count_hits_and_misses(board):
    hits = 0
    misses = 0
    for (y, x), val in np.ndenumerate(board):
        if 'H' in board[y][x] or 'S' in board[y][x]:
            hits += 1
        if board[y][x] == 'M':
            misses += 1

    return {'hits': hits, 'misses': misses}


def is_there_land(board):
    for cell in np.nditer(board):
        if cell == 'L':
            return True
    return False


def translate_coord_to_move(row, column):
    return {"Row": chr(row + 65), "Column": (column + 1)}


def translate_move_to_coord(move):
    return ord(move['Row']) - 65, move['Column'] - 1


