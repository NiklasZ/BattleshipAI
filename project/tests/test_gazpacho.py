import unittest
import numpy as np

import src.ai.bots.gazpacho as gaz


class TestNeighbourCoordinateRemoval(unittest.TestCase):
    # Testing the removal of available coordinates around a single coordinate. This includes the coordinate is well.
    def test_single_coord_removal(self):
        board = [['', 'B', ''],
                 ['E', 'A', 'C'],
                 ['', 'D', '']]

        available_coords = {(0, 0), (0, 1), (0, 2),
                            (1, 0), (1, 1), (1, 2),
                            (2, 0), (2, 1), (2, 2)}

        # The coordinates that should be left after removing the the neighbours and coordinate selected.
        test_coords_A = {(0, 0), (0, 2), (2, 0), (2, 2)}
        test_coords_B = {(1, 0), (1, 2), (2, 0), (2, 1), (2, 2)}
        test_coords_C = {(0, 0), (0, 1), (1, 0), (2, 0), (2, 1)}
        test_coords_D = {(0, 0), (0, 1), (0, 2), (1, 0), (1, 2)}
        test_coords_E = {(0, 1), (0, 2), (1, 2), (2, 1), (2, 2)}

        available_coords_A = set(available_coords)
        gaz.remove_neighbours((1, 1), available_coords_A, board)
        self.assertEqual(test_coords_A, available_coords_A)

        available_coords_B = set(available_coords)
        gaz.remove_neighbours((0, 1), available_coords_B, board)
        self.assertEqual(test_coords_B, available_coords_B)

        available_coords_C = set(available_coords)
        gaz.remove_neighbours((1, 2), available_coords_C, board)
        self.assertEqual(test_coords_C, available_coords_C)

        available_coords_D = set(available_coords)
        gaz.remove_neighbours((2, 1), available_coords_D, board)
        self.assertEqual(test_coords_D, available_coords_D)

        available_coords_E = set(available_coords)
        gaz.remove_neighbours((1, 0), available_coords_E, board)
        self.assertEqual(test_coords_E, available_coords_E)

    # Testing the removal of available coordinates around a ship.
    def test_ship_neighbour_removal(self):
        board = [['', 'B', 'B'],
                 ['', 'A', ''],
                 ['', 'A', '']]

        available_coords = {(0, 0), (0, 1), (0, 2),
                            (1, 0), (1, 1), (1, 2),
                            (2, 0), (2, 1), (2, 2)}

        ship_A_length = 2
        ship_A_orientation = 'V'
        ship_A_position = (1, 1)
        available_coords_A = set(available_coords)
        test_coords_A = {(0, 0), (0, 2)}

        ship_B_length = 2
        ship_B_orientation = 'H'
        ship_B_position = (0, 1)
        available_coords_B = set(available_coords)
        test_coords_B = {(1, 0), (2, 0), (2, 1), (2, 2)}

        gaz.remove_neighbouring_coords(ship_A_position, ship_A_orientation, available_coords_A, ship_A_length, board)
        self.assertEqual(test_coords_A, available_coords_A)

        gaz.remove_neighbouring_coords(ship_B_position, ship_B_orientation, available_coords_B, ship_B_length, board)
        self.assertEqual(test_coords_B, available_coords_B)


class TestRandomlySpacedShips(unittest.TestCase):
    # Try finding possible non-adjacent ship distributions 100 times on an empty board
    def test_empty_board(self):

        for i in range(100):
            board = [['', '', '', '', '', '', '', ''],
                     ['', '', '', '', '', '', '', ''],
                     ['', '', '', '', '', '', '', ''],
                     ['', '', '', '', '', '', '', ''],
                     ['', '', '', '', '', '', '', ''],
                     ['', '', '', '', '', '', '', ''],
                     ['', '', '', '', '', '', '', ''],
                     ['', '', '', '', '', '', '', '']]

            board = np.array(board)
            ships = [2, 3, 3, 4, 5]
            #print(gaz.randomly_space_ships(board, ships))
            #print(board)
            self.check_for_neighbours(board)

    # Helper method to check if any ship has neighbouring ships. If so, fail.
    def check_for_neighbours(self, board):
        for (y, x), val in np.ndenumerate(board):
            if val not in ['', 'L']:
                # Check above
                if y - 1 >= 0:
                    print()
                    self.assertTrue(board[y - 1, x] in ['', 'L', val])
                # Check below
                if y + 1 < len(board):
                    self.assertTrue(board[y + 1, x] in ['', 'L', val])
                # Check left
                if x - 1 >= 0:
                    self.assertTrue(board[y, x - 1] in ['', 'L', val])
                # Check right
                if x + 1 < len(board[0]):
                    self.assertTrue(board[y, x + 1] in ['', 'L', val])

    # Try finding possible non-adjacent ship distributions 100 times on an a board with land
    def test_board_with_land(self):
        for i in range(100):
            board = [['', '', '', '', '', '', '', ''],
                     ['', '', '', '', '', '', '', ''],
                     ['', '', '', '', '', '', '', ''],
                     ['', '', '', '', '', 'L', 'L', 'L'],
                     ['', '', '', 'L', 'L', 'L', '', ''],
                     ['', '', '', 'L', 'L', 'L', 'L', 'L'],
                     ['', '', 'L', 'L', 'L', 'L', 'L', 'L'],
                     ['', '', 'L', 'L', 'L', 'L', 'L', 'L']]

            board = np.array(board)
            ships = [2, 3, 3, 4, 5]
            #print(gaz.randomly_space_ships(board, ships))
            #print(board)
            self.check_for_neighbours(board)