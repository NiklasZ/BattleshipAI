from unittest import TestCase

import src.ai.bot_learning as learn


class TestBoardExtraction(TestCase):

    def test_finished_board(self):
        finished_board = [['', 'S0', 'S0', 'S0'],
                          ['', 'H', 'H', ''],
                          ['L', '', 'M', 'S1'],
                          ['', 'M', '', 'S1']]

        original_board_test = [['', '0', '0', '0'],
                               ['', '', '', ''],
                               ['L', '', '', '1'],
                               ['', '', '', '1']]

        self.assertEqual(original_board_test, learn._extract_original_opp_board(finished_board))

