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


class TestHitsAndMisses(unittest.TestCase):

    def test_count_no_hits_or_misses(self):

        board = [['', '', '2'],
                 ['', 'L', '2'],
                 ['1', '1', '']]

        test_hits = 0
        test_misses = 0

        results = src.ai.board_info.count_hits_and_misses(board)
        self.assertEqual(test_hits,results['hits'])
        self.assertEqual(test_misses, results['misses'])

    def test_count_hits_misses(self):
        board = [['H', '', 'S2'],
                 ['H', 'L', 'S2'],
                 ['1', 'H1', 'M']]

        test_hits = 5
        test_misses = 1

        results = src.ai.board_info.count_hits_and_misses(board)
        self.assertEqual(test_hits, results['hits'])
        self.assertEqual(test_misses, results['misses'])

class TestShipsAfloat(unittest.TestCase):

    # Test where the ships should be the same as nothing has been sunk.
    def test_no_ships(self):
        board = [['', 'H', '', '', ''],
                 ['', 'H', '', 'H', ''],
                 ['L', '', 'M', '', ''],
                 ['', '', '', '', 'H'],
                 ['', 'M', '', '', 'H']]

        ships = [2,3,4,5]

        test_afloat = [2,3,4,5]

        self.assertEqual(test_afloat, src.ai.board_info.ships_still_afloat(ships, board))

    # Test where some ships are sunk.
    def test_some_ships(self):
        board = [['', 'S0', '', '', 'S3'],
                 ['', 'S0', '', 'H', 'S3'],
                 ['L', '', 'M', '', 'S3'],
                 ['', '', '', '', 'S3'],
                 ['', 'M', '', '', 'S3']]

        ships = [2,3,4,5]

        test_afloat = [3,4]

        self.assertEqual(test_afloat, src.ai.board_info.ships_still_afloat(ships, board))

    # Test where a few ship lengths are repeated.
    def test_repeated_ship_lengths(self):
        board = [['', 'S1', '', '', ''],
                 ['', 'S1', '', 'H', ''],
                 ['L', 'S1', 'M', '', ''],
                 ['', '', '', '', 'H'],
                 ['', 'M', '', '', 'H']]

        ships = [2,3,3,4,5]

        test_afloat = [2,3,4,5]

        self.assertEqual(test_afloat, src.ai.board_info.ships_still_afloat(ships, board))

if __name__ == '__main__':
    unittest.main()
