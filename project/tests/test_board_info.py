import unittest

import src.ai
import src.ai.ship_deployment
import src.ai.board_info

import numpy as np


class BoardTranslation(unittest.TestCase):

    # Test if board indices translate to a battleship coordinate.
    def test_coord_translation(self):
        y = 0
        x = 3

        test_y = 'A'
        test_x = 4
        test_dict = {'Row': test_y, 'Column': test_x}

        self.assertEqual(test_dict, src.ai.board_info.translate_coord_to_move(y, x))

    # Test if a battleship translates into a pair of board indices.
    def test_move_translation(self):
        y = 'E'
        x = 5
        move_dict = {'Row': y, 'Column': x}

        test_y = 4
        test_x = 4

        self.assertEqual((test_y, test_x), src.ai.board_info.translate_move_to_coord(move_dict))


class LandTesting(unittest.TestCase):

    # Test if presence of land is correctly detected.
    def test_when_there_is_land(self):
        board = [['L', 'L', 'L'],
                 ['L', 'S2', 'H'],
                 ['M', '1', '']]

        board = np.array(board)

        self.assertTrue(src.ai.board_info.is_there_land(board))

    # Test if absence of land is correctly detected.
    def test_when_there_is_no_land(self):
        board = [['', '', ''],
                 ['', 'H', 'M'],
                 ['1', 'S2', '']]

        board = np.array(board)

        self.assertFalse(src.ai.board_info.is_there_land(board))


if __name__ == '__main__':
    unittest.main()
