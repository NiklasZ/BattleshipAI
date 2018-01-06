import numpy as np


def ships_still_afloat(ships, board):
    """
    Calculates how many of the available ships on the board have not yet been sunk.
    :param ships: a list of ships by length.
    :param board: the board to be inspected.
    :return: the list of ships not yet sunk.
    """
    afloat = []
    ships_removed = []
    for k in range(len(ships)):  # For every ship
        afloat.append(ships[k])  # Add it to the list of afloat ships
        ships_removed.append(False)  # Set its removed from afloat list to false
    for i in range(len(board)):
        for j in range(len(board[0])):  # For every grid on the board
            for k in range(len(ships)):  # For every ship
                if str(k) in board[i][j] and not ships_removed[
                    k]:  # If we can see the ship number on our opponent's board and we haven't already removed it from the afloat list
                    afloat.remove(ships[
                                      k])  # Remove that ship from the afloat list (we can only see an opponent's ship number when the ship has been sunk)
                    ships_removed[
                        k] = True  # Record that we have now removed this ship so we know not to try and remove it again
    return afloat  # Return the list of ships still afloat


def count_hits_and_misses(board):
    """
    Counts the how many shots on the boards hit a ship and how many didn't.
    :param board: the board to inspect.
    :return: a dict of the # of hits and # of misses.
    """
    hits = 0
    misses = 0
    for (y,x),val in np.ndenumerate(board):
        if 'H' in val or 'S' in val:
            hits += 1
        if val == 'M':
            misses += 1

    return {'hits': hits, 'misses': misses}


def is_there_land(board):
    """
    Checks if the playing board contains any land (L) cells.
    :param board: the board to inspect.
    :return: True if there is an L and false otherwise.
    """
    for cell in np.nditer(board):
        if cell == 'L':
            return True
    return False


def translate_coord_to_move(row, column):
    """
    Translates a pair of board indices to a move on a board. For example: (0,0) ==> {'Row':A,'Column':1}
    :param row: 1st index
    :param column: 2nd index
    :return: dict of the row and column.
    """
    return {"Row": chr(row + 65), "Column": (column + 1)}


def translate_move_to_coord(move):
    """
    Translates a move on a bord into a pair of indices. For example:  {'Row':A,'Column':1} ==> (0,0)
    :param move: a dict of the move.
    :return: the pair of indices.
    """
    return ord(move['Row']) - 65, move['Column'] - 1


