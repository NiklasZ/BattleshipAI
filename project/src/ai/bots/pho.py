# The Pho is the 3rd completed bot.
# It functions like Gazpacho in the defensive and offensive, but allows offensive play to be altered by heuristics.
# These heuristics then modify ship alignments to score moves. This bot will function with any heuristics that meet
# the specified standards. Without them, it will mostly mirror Gazpacho's behaviour.

# project imports
import src.ai.ship_targeting as ship_target
import src.ai.board_info as board_info
import src.ai.ship_deployment as ship_deploy

# library imports
from random import choice
import numpy as np


class Bot:
    """The Bot class, allowing the creation of an instance of the Pho bot."""
    def __init__(self):
        self.bot_name = 'Pho'
        self.heuristics = []
        self.last_choices = None

    def set_heuristics(self, heuristics):
        """
        Set the heuristics of the bot.
        :param heuristics: a list of tuples containing (heuristic function, heuristic value)
        :return:
        """
        self.heuristics = heuristics

    def make_move(self, game_state):
        """
        This function decides where to launch the next shot on the opponent board.
        :param game_state: A game_state dictionary, which conforms to the aigaming format.
        :return: A coordinate dict, containing a Row, Column and Orientation to fire at. E.g {"Row":"C", Column:1}.
        """
        opp_ships = np.array(board_info.ships_still_afloat(game_state['Ships'], game_state['OppBoard']))
        opp_board = np.array(game_state['OppBoard'])

        # If there are hits, try nearby targets.
        if 'H' in opp_board:

            moves = self._possible_hits(opp_board, opp_ships)

            # Select by highest sequence length.
            max_len_pos = max(moves, key=lambda x: moves[x]['seq_length'])
            max_length = moves[max_len_pos]['seq_length']
            length_choices = {k: v for k, v in moves.items() if v['seq_length'] == max_length}

            # Then select by highest heuristic score.
            max_fit_pos = max(length_choices, key=lambda x: length_choices[x]['score'])
            max_fit = length_choices[max_fit_pos]['score']
            choices = [move for move in length_choices if length_choices[move]['score'] == max_fit]
        # If not, search for possible targets from the grid.
        else:
            moves = self._possible_targets(opp_board, opp_ships)
            # Choose ones with highest score.
            highest = max(moves, key=lambda x: moves[x])
            choices = [move for move in moves if moves[move] == moves[highest]]

        self.last_choices = choices
        y, x = choice(choices)
        return board_info.translate_coord_to_move(y, x)

    def place_ships(self, game_state):
        """
        This function is called to place ships for the bot. In this case, it tries to first find a positioning that
        allows placing all ships so they are non-adjacent.
        :param game_state:  A game_state dictionary, which conforms to the aigaming format.
        :return: A dictionary of ship coordinates of the form:
        {"Placements":[{"Row":"C", Column:1, Orientation: "H"},...]}
        """
        ships = game_state['Ships']
        player_board = game_state['MyBoard']
        result = ship_deploy.randomly_space_ships(player_board, ships)

        # In case it is impossible to place the ships in a non-adjacent way.
        if result is None:
            return ship_deploy.deploy_randomly(ships, player_board)

        return ship_deploy.format_ship_deployment(result)

    def _possible_hits(self, opp_board, opp_ships):
        """
        Helper function that first obtains all coordinates adjacent to hits and then for each one computes the score.
        :param opp_board: a 2D numpy array containing a string representation of the board.
        :param opp_ships: a list of ints, where each int is the length of a ship on the board.
        :return: a dictionary of the structure {coordinate_of_hit:{possible_alignments:some_int, other vars...}}.
        E.g {(1,1):{"possible_alignments":4,...}
        """
        hit_options = ship_target.adjacent_to_hits(opp_board)
        for hit in hit_options:
            possible_ship_count = ship_target.possible_hit_scores(opp_board, opp_ships, hit, hit_options[hit],
                                                                  self.heuristics)
            hit_options[hit]['score'] = possible_ship_count
        return hit_options

    def _possible_targets(self, opp_board, opp_ships):
        """
        A helper function that finds scores for each coordinate on the board.
        It then restructures these into a dictionary, returning only coordinates with scores < 0.
        :param opp_board: a 2D numpy array containing a string representation of the board.
        :param opp_ships: a list of ints, where each int is the length of a ship on the board.
        :return: a dictionary of the structure {coordinate:number_of_alignments}. E.g {(0,0):1}
        """
        scores = ship_target.targeting_scores(opp_board, opp_ships, self.heuristics)
        # Get all non-zero possible scores and their indices.
        targets = {(y, x): val for y, row in enumerate(scores) for x, val in enumerate(row)}
        return targets
