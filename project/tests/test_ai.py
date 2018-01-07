from unittest import TestCase
import src.ai.ai as ai


class TestIsGameOver(TestCase):
    def test_is_game_over_no_state(self):
        game_state = None
        self.assertFalse(ai.is_game_over(game_state))

    def test_is_game_over_False_with_state(self):
        game_state = {}
        game_state['Ships'] = [5, 4, 3, 3, 2]
        game_state['MyBoard'] = [['', '1', '1', '1', '1', '', '', ''],
                                 ['', '', '', '', '', 'L', 'L', ''],
                                 ['', '2', '2', '2', 'L', 'L', 'L', ''],
                                 ['', '', '', 'L', 'L', 'L', 'L', ''],
                                 ['', '', '', 'L', 'L', 'L', '', ''],
                                 ['3', '3', '3', 'L', 'L', '4', '4', ''],
                                 ['', '', '', 'L', 'L', '', '', ''],
                                 ['', '', '', '0', '0', '0', '0', '0']]

        game_state['OppBoard'] = [['', '', '', '', '', '', '', ''],
                                  ['', '', '', '', '', 'L', 'L', ''],
                                  ['', '', '', '', 'L', 'L', 'L', ''],
                                  ['', '', '', 'L', 'L', 'L', 'L', ''],
                                  ['', '', '', 'L', 'L', 'L', '', ''],
                                  ['', '', '', 'L', 'L', '', '', ''],
                                  ['', '', '', 'L', 'L', '', '', ''],
                                  ['', '', '', '', '', '', '', '']]

        self.assertFalse(ai.is_game_over(game_state))