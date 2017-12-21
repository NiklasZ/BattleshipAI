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


class TestHeuristicAdjacency(TestCase):

    # Check if the function can find all the cells next to a hit or sunk ship.
    def test_cells_next_to_ship(self):
        board = [['', '', 'S2', 'S2'],
                 ['', 'H', '', ''],
                 ['L', '', 'M', ''],
                 ['H', 'M', '', 'H']]
        board = np.array(board)

        neighbours_cells_test = {(0, 1),
                                 (1, 0), (1, 2), (1, 3),
                                 (2, 1), (2, 3),
                                 (3, 2)}

        neighbours = learn.get_cells_adjacent_to_ships(board)

        self.assertEqual(neighbours, neighbours_cells_test)

    # Test if the scoring changes as expected for a ship adjacency of 0.5 (we assume adjacent ships are less likely).
    def test_ship_adjacency_low(self):
        ships = [2, 3, 4]
        board = [['', '', '', ''],
                 ['', 'H', '', ''],
                 ['L', '', 'M', ''],
                 ['', 'M', '', '']]

        # Means that ships:
        # (y:0,x:0,length:2,orientation:H), (y:0,x:0,length:3,orientation:H), (y:0,x:0,length:4,orientation:H)
        # (y:0,x:0,length:2,orientation:V)
        # (y:0,x:1,length:2,orientation:H), (y:0,x:1,length:3,orientation:H)
        # (y:0,x:2,length:2,orientation:V)
        # (y:1,x:2,length:2,orientation:H)
        # are now scored at 0.5 of their alignment.
        scores_test = [[2, 2.5, 3.5, 5],
                       [0, 0, 1, 5.5],
                       [0, 0, 0, 5],
                       [0, 0, 0, 4]]

        board = np.array(board)
        adj_weight = 0.5
        heuristic = (learn.ship_adjacency_heuristic, [adj_weight, board])

        scores = learn.get_targeting_scores(board, ships, [heuristic])
        for row, row_t in zip(scores, scores_test):
            for a, a_t in zip(row, row_t):
                self.assertEqual(a, a_t)
        self.assertEqual(np.sum(scores), np.sum(scores_test))

    # Test if the scoring changes as expected for a ship adjacency of 2 (we assume adjacent ships are more likely).
    def test_ship_adjacency_high(self):
        ships = [2, 3, 4]
        board = [['', '', '', ''],
                 ['', 'H', '', ''],
                 ['L', '', 'M', ''],
                 ['', 'M', '', '']]

        # Means that ships:
        # (y:0,x:0,length:2,orientation:H), (y:0,x:0,length:3,orientation:H), (y:0,x:0,length:4,orientation:H)
        # (y:0,x:0,length:2,orientation:V)
        # (y:0,x:1,length:2,orientation:H), (y:0,x:1,length:3,orientation:H)
        # (y:0,x:2,length:2,orientation:V)
        # (y:1,x:2,length:2,orientation:H)
        # are now scored at 2 of their alignment.
        scores_test = [[8, 10, 11, 8],
                       [0, 0, 4, 7],
                       [0, 0, 0, 5],
                       [0, 0, 0, 4]]

        board = np.array(board)
        adj_weight = 2
        heuristic = (learn.ship_adjacency_heuristic, [adj_weight, board])

        scores = learn.get_targeting_scores(board, ships, [heuristic])
        for row, row_t in zip(scores, scores_test):
            for a, a_t in zip(row, row_t):
                self.assertEqual(a, a_t)
        self.assertEqual(np.sum(scores), np.sum(scores_test))
