import src.ai.board_info as board_info

import copy
import numpy as np
import time
import queue
import random
import importlib

BOARD_SAMPLES = 100  # Number of boards to sample from a game

def init_bfs(bot_location, heuristics, opp_board, ships, state_limit, randomise=True):
    bot = getattr(importlib.import_module(bot_location), 'Bot')()
    bot.set_heuristics(heuristics)

    #start = time.time()
    games = bfs_games(bot, opp_board, ships, state_limit, randomise)
    #print('Time taken:', '{:.3f}'.format(time.time() - start) + 's')
    return games


def bfs_games(bot, opp_board, ships, state_limit, randomise):
    masked_opp_board = mask_board(opp_board)
    states = queue.Queue()
    root = (opp_board, masked_opp_board)
    leaves = []
    states.put(root)

    while states.qsize() > 0 and len(leaves) + states.qsize() < state_limit:
        node = states.get()

        game_state = {'Ships': ships, 'OppBoard': node[1]}
        bot.make_move(game_state)

        for choice in bot.last_choices:
            opp_board_copy = copy.deepcopy(node[0])
            masked_opp_board_copy = copy.deepcopy(node[1])
            shoot_at_opponent(choice, opp_board_copy, masked_opp_board_copy, ships)

            if has_won(opp_board_copy):
                leaves.append(masked_opp_board_copy)
            else:
                states.put((opp_board_copy, masked_opp_board_copy))

    while states.qsize() > 0:
        node = states.get()
        while not has_won(node[0]):
            game_state = {'Ships': ships, 'OppBoard': node[1]}
            bot.make_move(game_state)
            if randomise:
                choice = random.choice(bot.last_choices)
            else:
                choice = bot.last_choices[0]

            shoot_at_opponent(choice, node[0], node[1], ships)

        leaves.append(node[1])

    # unique = set()
    # for leaf in leaves:
    #     tuple = make_into_tuples(leaf)
    #     unique.add(tuple)
    #
    # hit_count = 0
    # miss_count = 0
    #
    # for leaf in leaves:
    #     result = board_info.count_hits_and_misses(leaf)
    #     hit_count += result['hits']
    #     miss_count += result['misses']

    # print('Final states found:', len(leaves))
    # print('Unique states found:', len(unique))
    # print('Hits:', hit_count, 'Misses:', miss_count)
    return leaves


def shoot_at_opponent(coord, opp_board, opponent_masked_board, ships):
    y, x = coord
    val = opp_board[y][x]
    if len(val) == 0:
        opponent_masked_board[y][x] = opp_board[y][x] = 'M'
    elif val.isdigit():
        opp_board[y][x] = 'H' + val
        opponent_masked_board[y][x] = 'H'
        check_if_sunk(int(val), opp_board, opponent_masked_board, ships)


# Check if a ship that has been shot will now sink and if so, modify the board.
def check_if_sunk(ship_no, opp_board, opponent_masked_board, ships):
    count = 0
    for (y, x), val in np.ndenumerate(opp_board):
        if val == 'H' + str(ship_no):
            count += 1

    if ships[ship_no] == count:
        for (y, x), val in np.ndenumerate(opp_board):
            if val == 'H' + str(ship_no):
                opp_board[y][x] = opponent_masked_board[y][x] = 'S' + str(ship_no)


def mask_board(board):
    masked = copy.deepcopy(board)
    for (y, x), val in np.ndenumerate(board):
        if val.isdigit():
            masked[y][x] = ''

    return masked


def has_won(board):
    for (y, x), val in np.ndenumerate(board):
        if val.isdigit():
            return False

    return True


def make_into_tuples(board):
    return tuple(tuple(e) for e in board)


def main():
    import importlib

    bot_location = 'src.ai.bots' + '.pho'
    bot = getattr(importlib.import_module(bot_location), 'Bot')()
    opp_board_1 = [['L', 'L', 'L', 'L', '', '', '3', ''],
                   ['L', 'L', 'L', 'L', 'L', 'L', '3', ''],
                   ['4', '4', 'L', 'L', 'L', 'L', '3', ''],
                   ['', '', '', 'L', 'L', '0', '', ''],
                   ['2', '2', '2', '', '', '0', '', ''],
                   ['', '', '', '', '', '0', '', ''],
                   ['1', '1', '1', '1', '', '0', '', ''],
                   ['', '', '', '', '', '0', '', '']]

    ships_1 = [5, 4, 3, 3, 2]
    opp_board_2 = [['', '', '', ''],
                   ['', '', '', ''],
                   ['', '0', '0', '0'],
                   ['', '', '', '']]

    ships_2 = [3]

    opp_board_3 = [['', '1', '', '', '', ''],
                   ['', '1', '', '', '', ''],
                   ['', '1', '', '', '', ''],
                   ['', '', '0', '0', '0', '0'],
                   ['', '', '', '', '', ''],
                   ['2', '2', '', '', '', '']]

    ships_3 = [4, 3, 2]

    opp_board_4 = [['1', '', '2', '2'],
                   ['1', '', '', ''],
                   ['', '0', '0', '0'],
                   ['', '', '', '']]

    ships_4 = [3, 2, 2]

    opp_board_5 = [['', '', '', '', '', '', '3', ''],
                   ['', '', '', '', '', '', '3', ''],
                   ['4', '4', '', '', '', '', '3', ''],
                   ['', '', '', '', '', '0', '', ''],
                   ['2', '2', '2', '', '', '0', '', ''],
                   ['', '', '', '', '', '0', '', ''],
                   ['1', '1', '1', '1', '', '0', '', ''],
                   ['', '', '', '', '', '0', '', '']]

    ships_5 = [5, 4, 3, 3, 2]

    # init_dfs(bot, opp_board_5, ships_5)
    init_bfs(bot_location, [], opp_board_5, ships_5, 100)


if __name__ == "__main__":
    main()
