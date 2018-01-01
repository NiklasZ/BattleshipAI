# Plays moves with bots
import src.ai.board_info as board_info

import importlib
import numpy as np
import copy


class GameSimulator:
    def __init__(self, bot_location, player_board, opponent_board, ships, heuristics=None):
        self.bot = getattr(importlib.import_module(bot_location), 'Bot')()
        self.player_board = player_board
        self.opponent_board = opponent_board
        self.opponent_masked_board = self.mask_board(self.opponent_board)
        self.ships = ships

        set_heuristics = getattr(self.bot, "set_heuristics", None)

        # Check if the bot has a heuristics setting function.
        if callable(set_heuristics) and heuristics:
            set_heuristics(heuristics)
        else:
            print('Bot',self.bot.bot_name,'does not use heuristics.')

    def attack_until_win(self):
        while not self.has_won(self.opponent_board):
            self.attack_opponent()

    # Have the bot choose a coordinate to attack.
    def attack_opponent(self):
        game_state = {'Ships': self.ships, 'OppBoard': self.opponent_masked_board, 'MyBoard': self.player_board}

        move = self.bot.make_move(game_state)
        coord = board_info.translate_move_to_coord(move)
        self.shoot_at_opponent(coord)

    # Modify the board based on where the shot hit.
    def shoot_at_opponent(self, coord,):
        y, x = coord
        val = self.opponent_board[y][x]
        if len(val) == 0:
            self.opponent_masked_board[y][x] = self.opponent_board[y][x] = 'M'
        elif val.isdigit():
            self.opponent_board[y][x] = 'H' + val
            self.opponent_masked_board[y][x] = 'H'
            self.check_if_sunk(int(val))

    # Check if a ship that has been shot will now sink and if so, modify the board.
    def check_if_sunk(self, ship_no):
        count = 0
        for (y, x), val in np.ndenumerate(self.opponent_board):
            if val == 'H' + str(ship_no):
                count += 1

        if self.ships[ship_no] == count:
            for (y, x), val in np.ndenumerate(self.opponent_board):
                if val == 'H' + str(ship_no):
                    self.opponent_board[y][x] = self.opponent_masked_board[y][x] = 'S' + str(ship_no)

    def mask_board(self, board):
        masked = copy.deepcopy(board)
        for (y, x), val in np.ndenumerate(board):
            if val.isdigit():
                masked[y][x] = ''

        return masked



    def has_won(self, board):
        for (y, x), val in np.ndenumerate(board):
            if val.isdigit():
                return False

        return True

