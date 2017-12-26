from unittest import TestCase

import numpy as np

import src.ai.ship_targeting as ship_target
import src.ai.heuristics as heur


class TestHeuristicAdjacency(TestCase):

    # Check if the function can find all the cells next to a hit or sunk ship.
    def test_cells_next_to_ship(self):
        board = [['', '', 'S2', 'S2'],
                 ['', 'S1', '', ''],
                 ['L', '', 'M', ''],
                 ['S3', 'M', '', 'S4']]
        board = np.array(board)

        neighbours_cells_test = {(0, 1),
                                 (1, 0), (1, 2), (1, 3),
                                 (2, 1), (2, 3),
                                 (3, 2)}

        neighbours = heur._get_cells_adjacent_to_ships(board)

        self.assertEqual(neighbours, neighbours_cells_test)

    # Test if the target scoring changes as expected for a ship adjacency of 0.5 (we assume adjacent ships are less likely).
    def test_targeting_ship_adjacency_low(self):
        ships = [2, 3, 4]
        board = [['', '', '', ''],
                 ['', 'S1', '', ''],
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
        heuristic = (heur.ship_adjacency, adj_weight)

        scores = ship_target.get_targeting_scores(board, ships, [heuristic])
        for row, row_t in zip(scores, scores_test):
            for a, a_t in zip(row, row_t):
                self.assertEqual(a, a_t)
        self.assertEqual(np.sum(scores), np.sum(scores_test))

    # Test if the target scoring changes as expected for a ship adjacency of 2 (we assume adjacent ships are more likely).
    def test_targeting_ship_adjacency_high(self):
        ships = [2, 3, 4]
        board = [['', '', '', ''],
                 ['', 'S1', '', ''],
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
        heuristic = (heur.ship_adjacency, adj_weight)

        scores = ship_target.get_targeting_scores(board, ships, [heuristic])
        for row, row_t in zip(scores, scores_test):
            for a, a_t in zip(row, row_t):
                self.assertEqual(a, a_t)
        self.assertEqual(np.sum(scores), np.sum(scores_test))

    # Test if the hit scoring changes as expected for a ship adjacency of 0.5 (we assume adjacent ships are less likely).
    def test_hitting_ship_adjacency_low(self):
        ships = [2, 3]
        board = [['', '', '', 'S0', ''],
                 ['', 'H', '', 'S0', ''],
                 ['L', '', 'M', '', ''],
                 ['', 'M', '', '', ''],
                 ['', 'M', '', '', '']]

        board = np.array(board)

        adj_weight = 0.5
        heuristic = (heur.ship_adjacency, adj_weight)

        pos_1 = (0, 1)
        hit_option_1 = {'seq_length': 1, 'direction': 'top'}
        test_score_1 = 2
        pos_2 = (1, 0)
        hit_option_2 = {'seq_length': 1, 'direction': 'left'}
        test_score_2 = 2
        pos_3 = (1, 2)
        # In this case, the adjacency to another ship halves the scoring of the ships.
        hit_option_3 = {'seq_length': 1, 'direction': 'right'}
        test_score_3 = 1
        pos_4 = (2, 1)
        hit_option_4 = {'seq_length': 1, 'direction': 'bottom'}
        test_score_4 = 2

        res_1 = ship_target.possible_hit_scores(board, ships, pos_1, hit_option_1, [heuristic])
        self.assertEqual(res_1, test_score_1)
        res_2 = ship_target.possible_hit_scores(board, ships, pos_2, hit_option_2, [heuristic])
        self.assertEqual(res_2, test_score_2)
        res_3 = ship_target.possible_hit_scores(board, ships, pos_3, hit_option_3, [heuristic])
        self.assertEqual(res_3, test_score_3)
        res_4 = ship_target.possible_hit_scores(board, ships, pos_4, hit_option_4, [heuristic])
        self.assertEqual(res_4, test_score_4)