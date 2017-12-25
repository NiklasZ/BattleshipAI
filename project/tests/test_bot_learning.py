from unittest import TestCase
import src.ai.bot_learning as learn
import numpy as np


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

        scores = learn.get_targeting_scores(board, ships, [])
        for row, row_t in zip(scores, scores_test):
            for a, a_t in zip(row, row_t):
                self.assertEqual(a, a_t)
        self.assertEqual(np.sum(scores), np.sum(scores_test))


