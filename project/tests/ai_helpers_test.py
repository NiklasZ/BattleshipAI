import unittest
import src.ai.ai_helpers as ai_help
import numpy as np


class TestDeployment(unittest.TestCase):

    # Check if it will reject invalid deployments.
    def test_deployment_reject(self):
        board = [['', '2', '2'],
                 ['', '1', ''],
                 ['', '1', '']]
        self.assertFalse(ai_help.can_deploy(0, 0, board, 2, 'H'))
        self.assertFalse(ai_help.can_deploy(0, 0, board, 4, 'V'))
        self.assertFalse(ai_help.can_deploy(1, 1, board, 1, 'V'))
        self.assertFalse(ai_help.can_deploy(1, 1, board, 1, 'H'))
        self.assertFalse(ai_help.can_deploy(2, 2, board, 2, 'V'))
        self.assertFalse(ai_help.can_deploy(2, 2, board, 2, 'H'))

    # Check if it will accept valid deployments
    def test_deployment_accept(self):
        board = [['', '', '', ''],
                 ['', '1', '', ''],
                 ['', '1', '', '']]
        self.assertTrue(ai_help.can_deploy(0, 0, board, 2, 'H'))
        self.assertTrue(ai_help.can_deploy(0, 1, board, 2, 'H'))
        self.assertTrue(ai_help.can_deploy(0, 0, board, 4, 'H'))
        self.assertTrue(ai_help.can_deploy(0, 0, board, 3, 'V'))
        self.assertTrue(ai_help.can_deploy(0, 2, board, 3, 'V'))
        self.assertTrue(ai_help.can_deploy(0, 3, board, 3, 'V'))


class TestAlignments(unittest.TestCase):
    # Check if the method gets the right number of alignments given ships and board.
    def test_single_board_alignment(self):
        ships = [2, 3]
        board = [['', '', '', '', ''],
                 ['', 'H', '', '', ''],
                 ['L', '', 'M', '', ''],
                 ['', 'M', '', '', ''],
                 ['', 'M', '', '', '']]
        self.assertEqual(ai_help.alignments_in(0, 0, board, ships), 3)
        self.assertEqual(ai_help.alignments_in(0, 4, board, ships), 4)
        self.assertEqual(ai_help.alignments_in(2, 1, board, ships), 0)

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

        alignments, alignment_sum = ai_help.possible_alignments(board, ships)
        for row, row_t in zip(alignments, alignments_test):
            for a, a_t in zip(row, row_t):
                self.assertEqual(a, a_t)
        self.assertEqual(alignment_sum, alignment_test_sum)


class TestHitSelection(unittest.TestCase):

    # Check whether it returns adjacent coordinates for single hits.
    def test_adjacent_selection(self):
        board = [['', '', '', '', ''],
                 ['', 'H', '', '', ''],
                 ['L', '', 'M', '', ''],
                 ['', 'M', '', '', ''],
                 ['', 'M', '', 'H', '']]
        ships = [2, 3]
        test_positions = [(0, 1), (1, 0), (1, 2), (2, 1), (3, 3), (4, 2), (4, 4)]

        hit_positions = ai_help.possible_hits(board, ships)
        for tp in test_positions:
            found = False
            for hit_pos in hit_positions.keys():
                if tp[0] == hit_pos[0] and tp[1] == hit_pos[1]:
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
        ships = [2, 3]
        test_positions = [(0, 0), (0, 2), (1, 0), (1, 2), (2, 1), (2, 3), (2, 4), (4, 0), (4, 2), (4, 4)]
        hit_positions = ai_help.possible_hits(board, ships)

        for tp in test_positions:
            found = False
            for hit_pos in hit_positions:
                if tp[0] == hit_pos[0] and tp[1] == hit_pos[1]:
                    found = True

            # Checks that all the required finds are there.
            self.assertTrue(found)
            # Checks that there are no extra finds.
            self.assertEqual(len(hit_positions), len(test_positions))

    def test_adjacent_selection_long_segments(self):
        board = [['', 'H', '', '', ''],
                 ['', 'H', '', '', ''],
                 ['L', '', 'M', '', ''],
                 ['H', 'M', 'H', 'H', 'H'],
                 ['', 'M', '', 'H', '']]
        ships = [2, 3]
        test_positions = [(0, 0, 1), (0, 2, 1), (1, 0, 1), (1, 2, 1), (2, 1, 2), (2, 3, 2), (2, 4, 1), (4, 0, 1),
                          (4, 2, 2), (4, 4, 2)]
        hit_positions = ai_help.possible_hits(board, ships)
        for tp in test_positions:
            found = False
            for hit_pos in hit_positions:
                if tp[0] == hit_pos[0] and tp[1] == hit_pos[1]:
                    self.assertEqual(tp[2], hit_positions[hit_pos])


if __name__ == '__main__':
    unittest.main()
