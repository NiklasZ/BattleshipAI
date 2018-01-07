# This module is home to an algorithm that explores a game tree of a battleship board, using a given bot. It then
# obtains a list of terminal states the board can arrive at. The purpose of this is to simulate the playing of probable
# games that can then be evaluated by a function which is in turn, optimised.

#Library imports
import copy
import numpy as np
import queue
import random
import importlib

BOARD_SAMPLES = 100  # Number of boards to sample from a board

def init_bfs(bot_location, heuristics, board, ships, state_limit=BOARD_SAMPLES, randomise=True):
    """
    This function loads a bot and then has it generate a game tree of the possible plays on the board. It initially
    traverses the tree in a bread-first search until it has found branches <= state_limit. Branches where each child is
    is also evaluated are not considered. Once it has a branch count <= state_limit, it then plays each branch to leaf/
    terminal state (where the game is won). It then returns these played boards.
    :param bot_location: a string of a module path to where the desired bot resides.
    :param heuristics: a list of heuristic tuples in the form: (heuristic function, heuristic weight). These are the
    parameters the optimisation algorithm should attempt to optimise.
    :param board: a 2D numpy array containing a string representation of the board. This should be a board showing the
    locations of all the ships in an non-sunk state.
    :param ships: a list of ints, where each int is the length of a ship on the board.
    :param state_limit: a number that sets an upper limit as to how many games to explore and return
    :param randomise: An extra parameter that decides whether to randomly choose from the bot's suggested moves as
    opposed to always picking the first one. Notably, this is only relevant when playing towards a terminal state.
    :return: a list of boards, where each board has all ships sunk.
    """
    bot = getattr(importlib.import_module(bot_location), 'Bot')() # load the bot
    bot.set_heuristics(heuristics) # set the bot's heuristics.

    games = _bfs_games(bot, board, ships, state_limit, randomise)
    return games


def _bfs_games(bot, board, ships, state_limit, randomise):
    """
    Performs a BFS on the board's possible states. Each iteration, it removes an element (board) and has the bot suggest
     a list of moves. It then performs each move and adds the new boards to the queue. After each move, it also has to
    check whether the game is already won (there are no ships left to sink). In this case, the new board is placed in a
     list of leaves instead of the queue. This continues until the length of leaves+queue == state_limit at which point
     we have found at least state_limit different games to evaluate.
     The 2nd part is then to evaluate the leftover elements in the queue until they also reach a terminal state (win).
     Once this is done, the leaves are returned.
    :param bot: A bot that can suggest moves and store them in bot.last_choices
    :param board: a 2D numpy array containing a string representation of the board. This should be a board showing the
    locations of all the ships in an non-sunk state.
    :param ships: a list of ints, where each int is the length of a ship on the board.
    :param state_limit: a number that sets an upper limit as to how many games to explore and return
    :param randomise: An extra parameter that decides whether to randomly choose from the bot's suggested moves as
    opposed to always picking the first one. Notably, this is only relevant when playing towards a terminal state.
    :return: a list of boards, where each board has all ships sunk.
    """
    masked_opp_board = _mask_board(board) # Create a copy of the board with the visible ships that hides them.
    states = queue.Queue() # A queue in which to store the boards
    root = (board, masked_opp_board) # the initial board.
    leaves = [] # a list of terminal/won boards.
    states.put(root)

    # Keep going as long as there are still states (it could happen that we evaluate every possible game before reaching
    # the limit). Additionally also stay within the state_limit.
    while states.qsize() > 0 and len(leaves) + states.qsize() < state_limit:
        node = states.get()

        # Make a game state and let the bot suggest moves for it.
        game_state = {'Ships': ships, 'OppBoard': node[1]}
        bot.make_move(game_state)

        # For each choice, make copy and evaluate it.
        for choice in bot.last_choices:
            opp_board_copy = copy.deepcopy(node[0])
            masked_opp_board_copy = copy.deepcopy(node[1])
            _shoot_at_opponent(choice, opp_board_copy, masked_opp_board_copy, ships) # shoot at the board.

            # If we have won, add it to leaves.
            if _has_won(opp_board_copy):
                leaves.append(masked_opp_board_copy)
            # Otherwise, add it to the states.
            else:
                states.put((opp_board_copy, masked_opp_board_copy))

    # After we have enough states, evaluate each state until the game is won.
    while states.qsize() > 0:
        node = states.get()
        while not _has_won(node[0]):
            game_state = {'Ships': ships, 'OppBoard': node[1]}
            bot.make_move(game_state)
            # Choose the next move randomly, or let it be the first of the possible options.
            if randomise:
                choice = random.choice(bot.last_choices)
            else:
                choice = bot.last_choices[0]

            _shoot_at_opponent(choice, node[0], node[1], ships) # modify the board to look shot at.

        leaves.append(node[1])

    return leaves # return finished games.


def _shoot_at_opponent(coord, board, masked_board, ships):
    """
    A function that simulates a shot being fired at the board and masked_board.
    :param coord: the coordinate that is being fired at.
    :param board: a 2D numpy array containing a string representation of the board. All ships should be visible.
    :param masked_board: a 2D numpy array containing a string representation of the board. Only hits and sunk ships
    should be visible.
    :param ships: a list of ints, where each int is the length of a ship on the board.
    :return: 
    """
    y, x = coord
    val = board[y][x]
    # If the coordinate is empty set it to a miss on both.
    if len(val) == 0:
        masked_board[y][x] = board[y][x] = 'M'
    # If it is not and the target is in fact a ship, set them as hit and check whether this has sunk the ship.
    elif val.isdigit():
        board[y][x] = 'H' + val
        masked_board[y][x] = 'H'
        _check_if_sunk(int(val), board, masked_board, ships)


def _check_if_sunk(ship_no, board, masked_board, ships):
    """
    A function that checks whether given ship (of id ship_no) has been hit entirely and should now be labelled as
    sunken.
    :param ship_no: the integer id of the ship.
    :param board: a 2D numpy array containing a string representation of the board. All ships should be visible.
    :param masked_board: a 2D numpy array containing a string representation of the board. Only hits and sunk ships
    should be visible.
    :param ships: a list of ints, where each int is the length of a ship on the board.
    :return:
    """
    # Count whether there are enough hit locations for the ship.
    count = 0
    for (y, x), val in np.ndenumerate(board):
        if val == 'H' + str(ship_no):
            count += 1

    # If there are, update these to now be sunken.
    if ships[ship_no] == count:
        for (y, x), val in np.ndenumerate(board):
            if val == 'H' + str(ship_no):
                board[y][x] = masked_board[y][x] = 'S' + str(ship_no)


def _mask_board(board):
    """
    A function that copies the inputted board replaces all ships with empty coordinates to mask them.
    :param board: a 2D numpy array containing a string representation of the board. All ships should be visible.
    :return: a 2D numpy array containing a string representation of the board, with all ships hidden.
    """
    masked = copy.deepcopy(board) # copy operation
    for (y, x), val in np.ndenumerate(board):
        if val.isdigit():
            masked[y][x] = ''

    return masked


def _has_won(board):
    """
    Checks if there are any non-sunk ships on the board. If so, returns False (as that means the game is not over yet).
    Otherwise returns True.
    :param board: a 2D numpy array containing a string representation of the board. All ships should be visible.
    :return: False, if game is not over. True otherwise.
    """
    for (y, x), val in np.ndenumerate(board):
        if val.isdigit():
            return False

    return True

# This is old testing code, please ignore.
# def main():
#     import importlib
#
#     bot_location = 'src.ai.bots' + '.pho'
#     bot = getattr(importlib.import_module(bot_location), 'Bot')()
#     opp_board_1 = [['L', 'L', 'L', 'L', '', '', '3', ''],
#                    ['L', 'L', 'L', 'L', 'L', 'L', '3', ''],
#                    ['4', '4', 'L', 'L', 'L', 'L', '3', ''],
#                    ['', '', '', 'L', 'L', '0', '', ''],
#                    ['2', '2', '2', '', '', '0', '', ''],
#                    ['', '', '', '', '', '0', '', ''],
#                    ['1', '1', '1', '1', '', '0', '', ''],
#                    ['', '', '', '', '', '0', '', '']]
#
#     ships_1 = [5, 4, 3, 3, 2]
#     opp_board_2 = [['', '', '', ''],
#                    ['', '', '', ''],
#                    ['', '0', '0', '0'],
#                    ['', '', '', '']]
#
#     ships_2 = [3]
#
#     opp_board_3 = [['', '1', '', '', '', ''],
#                    ['', '1', '', '', '', ''],
#                    ['', '1', '', '', '', ''],
#                    ['', '', '0', '0', '0', '0'],
#                    ['', '', '', '', '', ''],
#                    ['2', '2', '', '', '', '']]
#
#     ships_3 = [4, 3, 2]
#
#     opp_board_4 = [['1', '', '2', '2'],
#                    ['1', '', '', ''],
#                    ['', '0', '0', '0'],
#                    ['', '', '', '']]
#
#     ships_4 = [3, 2, 2]
#
#     opp_board_5 = [['', '', '', '', '', '', '3', ''],
#                    ['', '', '', '', '', '', '3', ''],
#                    ['4', '4', '', '', '', '', '3', ''],
#                    ['', '', '', '', '', '0', '', ''],
#                    ['2', '2', '2', '', '', '0', '', ''],
#                    ['', '', '', '', '', '0', '', ''],
#                    ['1', '1', '1', '1', '', '0', '', ''],
#                    ['', '', '', '', '', '0', '', '']]
#
#     ships_5 = [5, 4, 3, 3, 2]
#
#     # init_dfs(bot, opp_board_5, ships_5)
#     init_bfs(bot_location, [], opp_board_5, ships_5, 100)
#
#
# if __name__ == "__main__":
#     main()
