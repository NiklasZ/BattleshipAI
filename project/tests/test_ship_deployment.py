import unittest

import src.ai


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

class TestShipTranslation(unittest.TestCase):

    # Check if a ship translates correctly to battleship standard.
    def test_ship_translation(self):
        ship_y = 1
        ship_x = 2
        ship_orientation = 'H'

        test_y = 'B'
        test_x = 3
        test_ship_orientation = 'H'
        test_dict = {'Row': test_y, 'Column': test_x, 'Orientation': test_ship_orientation}

        self.assertEqual(test_dict, src.ai.ship_deployment.translate_ship(ship_y, ship_x, ship_orientation))