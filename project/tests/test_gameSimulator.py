from unittest import TestCase
import src.utils.game_simulator as sim

import numpy as np


class TestGameSimulator(TestCase):

    def test_shoot_at_opponent(self):
        opp_board = [['0', '0', '0', '0', '', ''],
                     ['', '', '1', '', '', ''],
                     ['', '', '1', '', '', ''],
                     ['', 'L', '1', '', '', ''],
                     ['L', 'L', 'L', 'L', 'L', ''],
                     ['L', 'L', '2', '2', 'L', '']]

        player_board = [['', '', '', '', '', ''],
                        ['', '', '', '', '', ''],
                        ['', '', '', '', '', ''],
                        ['', 'L', '', '', '', ''],
                        ['L', 'L', 'L', 'L', 'L', ''],
                        ['L', 'L', '', '', 'L', '']]

        opp_board_test = [['H0', '0', 'H0', '0', '', ''],
                          ['M', '', '1', '', '', ''],
                          ['', '', '1', '', '', ''],
                          ['', 'L', '1', '', '', ''],
                          ['L', 'L', 'L', 'L', 'L', ''],
                          ['L', 'L', 'S2', 'S2', 'L', '']]

        opp_board_masked_test = [['H', '', 'H', '', '', ''],
                                 ['M', '', '', '', '', ''],
                                 ['', '', '', '', '', ''],
                                 ['', 'L', '', '', '', ''],
                                 ['L', 'L', 'L', 'L', 'L', ''],
                                 ['L', 'L', 'S2', 'S2', 'L', '']]

        ships = [4, 3, 2]

        game = init_simulator(player_board, opp_board, ships)
        # Test valid hits.
        game.shoot_at_opponent((0, 0))
        game.shoot_at_opponent((0, 0))  # a repeated shot should not change anything.
        game.shoot_at_opponent((0, 2))

        # Test valid misses.
        game.shoot_at_opponent((1, 0))
        game.shoot_at_opponent((1, 0))  # a repeated shot should not change anything.

        # Test shooting land.
        game.shoot_at_opponent((4, 1))
        game.shoot_at_opponent((4, 1))  # a repeated shot should not change anything.

        # Sink ship
        game.shoot_at_opponent((5, 2))
        game.shoot_at_opponent((5, 3))
        game.shoot_at_opponent((5, 3))  # a repeated shot should not change anything.

        self.assertEqual(opp_board_masked_test, game.opponent_masked_board)
        self.assertEqual(opp_board_test, game.opponent_board)

    def test_check_if_sunk(self):
        opp_board = [['0', '0', '0', '0', '', ''],
                     ['', '', '1', '', '', ''],
                     ['', '', '1', '', '', ''],
                     ['', 'L', '1', '', '', ''],
                     ['L', 'L', 'L', 'L', 'L', ''],
                     ['L', 'L', '2', '2', 'L', '']]

        player_board = [['', '', '', '', '', ''],
                        ['', '', '', '', '', ''],
                        ['', '', '', '', '', ''],
                        ['', 'L', '', '', '', ''],
                        ['L', 'L', 'L', 'L', 'L', ''],
                        ['L', 'L', '', '', 'L', '']]

        masked_sunk_test = [['S0', 'S0', 'S0', 'S0', '', ''],
                            ['', '', '', '', '', ''],
                            ['', '', '', '', '', ''],
                            ['', 'L', '', '', '', ''],
                            ['L', 'L', 'L', 'L', 'L', ''],
                            ['L', 'L', '', '', 'L', '']]

        sunk_test = [['S0', 'S0', 'S0', 'S0', '', ''],
                     ['', '', '1', '', '', ''],
                     ['', '', '1', '', '', ''],
                     ['', 'L', '1', '', '', ''],
                     ['L', 'L', 'L', 'L', 'L', ''],
                     ['L', 'L', '2', '2', 'L', '']]

        ships = [4, 3, 2]

        game = init_simulator(player_board, opp_board, ships)
        game.opponent_board[0][0] = game.opponent_board[0][1] = game.opponent_board[0][2] = game.opponent_board[0][
            3] = 'H0'
        game.check_if_sunk(0)
        game.check_if_sunk(1)
        game.check_if_sunk(2)
        self.assertTrue(np.array_equal(game.opponent_masked_board, masked_sunk_test))
        self.assertTrue(np.array_equal(game.opponent_board, sunk_test))

    def test_mask_board(self):
        opponent_board = [['0', '0', '0', '0', '', ''],
                          ['', '', '1', '', '', ''],
                          ['', '', '1', '', '', ''],
                          ['', 'L', '1', '', '', ''],
                          ['L', 'L', 'L', 'L', 'L', ''],
                          ['L', 'L', '2', '2', 'L', '']]

        player_board = [['', '', '', '', '', ''],
                        ['', '', '', '', '', ''],
                        ['', '', '', '', '', ''],
                        ['', 'L', '', '', '', ''],
                        ['L', 'L', 'L', 'L', 'L', ''],
                        ['L', 'L', '', '', 'L', '']]

        masked_test = [['', '', '', '', '', ''],
                       ['', '', '', '', '', ''],
                       ['', '', '', '', '', ''],
                       ['', 'L', '', '', '', ''],
                       ['L', 'L', 'L', 'L', 'L', ''],
                       ['L', 'L', '', '', 'L', '']]
        ships = [4, 3, 2]

        game = init_simulator(player_board, opponent_board, ships)
        masked = game.mask_board(game.opponent_board)

        self.assertTrue(np.array_equal(masked, masked_test))


def init_simulator(player_board, opp_board, ships, bot_name='gazpacho'):
    return sim.GameSimulator(bot_name, player_board, opp_board, ships)
