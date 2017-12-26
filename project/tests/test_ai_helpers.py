import unittest
from unittest import TestCase

import numpy as np

import src.ai
import src.ai.ship_deployment
import src.ai.ship_targeting as ai_help
import src.ai.board_info


class TestDeployment(unittest.TestCase):

    # Check if it will reject invalid deployments.
    def test_deployment_reject(self):
        board = [['', '2', '2'],
                 ['', '1', ''],
                 ['', '1', '']]
        self.assertFalse(src.ai.ship_deployment.can_deploy(0, 0, board, 2, 'H'))
        self.assertFalse(src.ai.ship_deployment.can_deploy(0, 0, board, 4, 'V'))
        self.assertFalse(src.ai.ship_deployment.can_deploy(1, 1, board, 1, 'V'))
        self.assertFalse(src.ai.ship_deployment.can_deploy(1, 1, board, 1, 'H'))
        self.assertFalse(src.ai.ship_deployment.can_deploy(2, 2, board, 2, 'V'))
        self.assertFalse(src.ai.ship_deployment.can_deploy(2, 2, board, 2, 'H'))

    # Check if it will accept valid deployments
    def test_deployment_accept(self):
        board = [['', '', '', ''],
                 ['', '1', '', ''],
                 ['', '1', '', '']]
        self.assertTrue(src.ai.ship_deployment.can_deploy(0, 0, board, 2, 'H'))
        self.assertTrue(src.ai.ship_deployment.can_deploy(0, 1, board, 2, 'H'))
        self.assertTrue(src.ai.ship_deployment.can_deploy(0, 0, board, 4, 'H'))
        self.assertTrue(src.ai.ship_deployment.can_deploy(0, 0, board, 3, 'V'))
        self.assertTrue(src.ai.ship_deployment.can_deploy(0, 2, board, 3, 'V'))
        self.assertTrue(src.ai.ship_deployment.can_deploy(0, 3, board, 3, 'V'))


class TestAlignments(unittest.TestCase):
    # Check if the method gets the right number of alignments given ships and board.
    def test_single_board_alignment(self):
        ships = [2, 3]
        board = [['', '', '', '', ''],
                 ['', 'H', '', '', ''],
                 ['L', '', 'M', '', ''],
                 ['', 'M', '', '', ''],
                 ['', 'M', '', '', '']]
        self.assertEqual(len(ai_help._alignments_in(0, 0, board, ships)), 3)
        self.assertEqual(len(ai_help._alignments_in(0, 4, board, ships)), 4)
        self.assertEqual(len(ai_help._alignments_in(2, 1, board, ships)), 0)

    # Check alignments on a whole board.
    def test_whole_board_alignment(self):
        ships = [2, 3, 4]
        board = [['', '', '', ''],
                 ['', 'H', '', ''],
                 ['L', '', 'M', ''],
                 ['', 'M', '', '']]
        alignments_test = [[4, 5, 6, 6],
                           [1, 0, 2, 6],
                           [0, 0, 0, 5],
                           [0, 0, 1, 4]]
        alignment_test_sum = 40

        alignments = ai_help.possible_alignments(board, ships)
        for row, row_t in zip(alignments, alignments_test):
            for a, a_t in zip(row, row_t):
                self.assertEqual(a, a_t)
        self.assertEqual(np.sum(alignments), alignment_test_sum)

    def test_whole_board_alignment_reduced(self):
        ships = [2, 3, 4]
        board = [['', '', '', ''],
                 ['', 'H', '', ''],
                 ['L', '', 'M', ''],
                 ['', 'M', '', '']]
        alignments_test = [[4, 5, 6, 6],
                           [0, 0, 2, 6],
                           [0, 0, 0, 5],
                           [0, 0, 0, 4]]
        alignment_test_sum = 38

        alignments = ai_help.possible_alignments(board, ships, reduce=True)
        for row, row_t in zip(alignments, alignments_test):
            for a, a_t in zip(row, row_t):
                self.assertEqual(a, a_t)
        self.assertEqual(np.sum(alignments), alignment_test_sum)


class TestHitSelection(unittest.TestCase):

    # Check whether it returns adjacent coordinates for single hits.
    def test_adjacent_selection(self):
        board = [['', '', '', '', ''],
                 ['', 'H', '', '', ''],
                 ['L', '', 'M', '', ''],
                 ['', 'M', '', '', ''],
                 ['', 'M', '', 'H', '']]
        test_positions = [(0, 1), (1, 0), (1, 2), (2, 1), (3, 3), (4, 2), (4, 4)]

        hit_positions = ai_help.adjacent_to_hits(board)
        for tp in test_positions:
            found = False
            if tp in hit_positions:
                found = True
            # Checks that all the required finds are there.
            self.assertTrue(found)

        # Checks that there are no extra finds.
        self.assertEqual(len(hit_positions), len(test_positions))

    # Check whether it returns adjacent coordinates for longer hits and
    # segments on the same column/row.
    def test_adjacent_selection_long_segments(self):
        board = [['', 'H', '', '', ''],
                 ['', 'H', '', '', ''],
                 ['L', '', 'M', '', ''],
                 ['H', 'M', 'H', 'H', 'H'],
                 ['', 'M', '', 'H', '']]
        test_positions = [(0, 0), (0, 2), (1, 0), (1, 2), (2, 1), (2, 3), (2, 4), (4, 0), (4, 2), (4, 4)]
        hit_positions = ai_help.adjacent_to_hits(board)

        for tp in test_positions:
            found = False
            if tp in hit_positions:
                found = True
            # Checks that all the required finds are there.
            self.assertTrue(found)
        # Checks that there are no extra finds.
        self.assertEqual(len(hit_positions), len(test_positions))

    # Check whether the length of the found segments is correct.
    def test_adjacent_selection_segment_length(self):
        board = [['', 'H', '', '', ''],
                 ['', 'H', '', '', ''],
                 ['L', '', 'M', '', ''],
                 ['H', 'M', 'H', 'H', 'H'],
                 ['', 'M', '', 'H', '']]
        test_positions = [(0, 0, 1), (0, 2, 1), (1, 0, 1), (1, 2, 1), (2, 1, 2), (2, 3, 2), (2, 4, 1), (4, 0, 1),
                          (4, 2, 2), (4, 4, 2)]
        hit_positions = ai_help.adjacent_to_hits(board)
        for tp in test_positions:
            if tp in hit_positions:
                self.assertEqual(tp[2], hit_positions['seq_length'])


class TestHitPossibilities(unittest.TestCase):

    # Test whether the possibilities work below a sequence.
    def test_hit_bottom(self):
        board = [['', 'H', '', '', ''],
                 ['', 'H', '', '', ''],
                 ['L', '', 'M', '', ''],
                 ['', '', '', 'H', ''],
                 ['', 'M', '', '', '']]
        ships = [2, 3, 4, 5]

        hit_pos_A = (2, 1)
        hit_option_A = {'seq_length': 2, 'direction': 'bottom'}
        test_count_A = 2  # The ship of length 2 is impossible as the length already is 2 and the length 5 does not fit.

        hit_pos_B = (3, 3)
        hit_option_B = {'seq_length': 1, 'direction': 'bottom'}
        test_count_B = 6  # 2 and 5 can only be fir in one alignment, whereas 3 and 4 have two possible alignments each.

        self.assertEqual(test_count_A, ai_help.possible_hit_ships(board, ships, hit_pos_A, hit_option_A))
        self.assertEqual(test_count_B, ai_help.possible_hit_ships(board, ships, hit_pos_B, hit_option_B))

    # Test whether the possibilities work on top of a sequence.
    def test_hit_top(self):
        board = [['', '', '', '', ''],
                 ['', 'H', '', '', ''],
                 ['L', '', 'M', '', ''],
                 ['', '', '', '', ''],
                 ['', 'M', '', '', 'H']]
        ships = [2, 3, 4, 5, 6]

        hit_pos_A = (3, 4)
        hit_option_A = {'seq_length': 1, 'direction': 'top'}
        test_count_A = 4  # The ship of length 1 is impossible as the length already is 1 and the length 6 does not fit.

        hit_pos_B = (0, 1)
        hit_option_B = {'seq_length': 1, 'direction': 'top'}
        test_count_B = 3  # There is 1 fit for each ship from 2-4

        self.assertEqual(test_count_A, ai_help.possible_hit_ships(board, ships, hit_pos_A, hit_option_A))
        self.assertEqual(test_count_B, ai_help.possible_hit_ships(board, ships, hit_pos_B, hit_option_B))

    # Test whether the possibilities work to the left of a sequence.
    def test_hit_right(self):
        board = [['', 'H', '', '', ''],
                 ['', 'H', '', '', ''],
                 ['L', '', 'M', '', ''],
                 ['', '', '', '', ''],
                 ['', 'M', '', 'H', '']]
        ships = [2, 3, 4, 5, 6]

        hit_pos_A = (0, 2)
        hit_option_A = {'seq_length': 1, 'direction': 'right'}
        test_count_A = 6  # ship 2 has one fit, ship 3 has two fits, ship 4 has two fits and ship 5 has 1 fit.

        hit_pos_B = (4, 4)
        hit_option_B = {'seq_length': 1, 'direction': 'right'}
        test_count_B = 2  # There is a fit for ships 2 & 3.

        self.assertEqual(test_count_A, ai_help.possible_hit_ships(board, ships, hit_pos_A, hit_option_A))
        self.assertEqual(test_count_B, ai_help.possible_hit_ships(board, ships, hit_pos_B, hit_option_B))

    # Test whether the possibilities work to the right of a sequence.
    def test_hit_left(self):
        board = [['', 'H', '', '', ''],
                 ['', 'H', '', '', ''],
                 ['L', '', 'M', '', ''],
                 ['', '', '', '', ''],
                 ['H', 'M', '', '', 'H']]
        ships = [1, 2, 3, 4, 5]

        hit_pos_A = (4, 3)
        hit_option_A = {'seq_length': 1, 'direction': 'left'}
        test_count_A = 2  # The ship of length 1 is impossible and only lengths 2,3 fit.

        hit_pos_B = (0, 0)
        hit_option_B = {'seq_length': 1, 'direction': 'left'}
        test_count_B = 4  # There is 1 fit for each ship from 2-5

        self.assertEqual(test_count_A, ai_help.possible_hit_ships(board, ships, hit_pos_A, hit_option_A))
        self.assertEqual(test_count_B, ai_help.possible_hit_ships(board, ships, hit_pos_B, hit_option_B))


class BoardTranslation(unittest.TestCase):

    def test_ship_translation(self):
        ship_y = 1
        ship_x = 2
        ship_orientation = 'H'

        test_y = 'B'
        test_x = 3
        test_ship_orientation = 'H'
        test_dict = {'Row': test_y, 'Column': test_x, 'Orientation': test_ship_orientation}

        self.assertEqual(test_dict, src.ai.ship_deployment.translate_ship(ship_y, ship_x, ship_orientation))

    def test_coord_translation(self):
        y = 0
        x = 3

        test_y = 'A'
        test_x = 4
        test_dict = {'Row': test_y, 'Column': test_x}

        self.assertEqual(test_dict, src.ai.board_info.translate_coord_to_move(y, x))

    def test_move_translation(self):
        y = 'E'
        x = 5
        move_dict = {'Row': y, 'Column': x}

        test_y = 4
        test_x = 4

        self.assertEqual((test_y, test_x), src.ai.board_info.translate_move_to_coord(move_dict))


if __name__ == '__main__':
    unittest.main()


class TestTargetingScores(TestCase):

    # If there are no heuristics it should behave like a regular reduced alignment.
    def test_alignment_no_heuristics(self):
        ships = [2, 3, 4]
        board = [['', '', '', ''],
                 ['', 'H', '', ''],
                 ['L', '', 'M', ''],
                 ['', 'M', '', '']]
        scores_test = [[4, 5, 6, 6],
                       [0, 0, 2, 6],
                       [0, 0, 0, 5],
                       [0, 0, 0, 4]]

        scores = src.ai.ship_targeting.get_targeting_scores(board, ships, [])
        for row, row_t in zip(scores, scores_test):
            for a, a_t in zip(row, row_t):
                self.assertEqual(a, a_t)
        self.assertEqual(np.sum(scores), np.sum(scores_test))