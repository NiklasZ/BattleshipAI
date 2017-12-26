
import src.ai.ship_targeting as ship_target
import src.ai.board_info as board_info
import src.ai.ship_deployment as ship_deploy

from random import choice
import numpy as np

class Bot:

    def __init__(self):
        self.bot_name = 'Gazpacho'

    def make_move(self, game_state):
        opp_ships = np.array(board_info.ships_still_afloat(game_state['Ships'], game_state['OppBoard']))
        opp_board = np.array(game_state['OppBoard'])

        # If there are hits, try nearby targets.
        if 'H' in opp_board:

            moves = _possible_hits(opp_board, opp_ships)

            # Select by highest sequence length.
            # highest_length = max(moves, key=lambda x: moves[x]['seq_length'])
            max_len_pos = max(moves, key=lambda x: moves[x]['seq_length'])
            max_length = moves[max_len_pos]['seq_length']
            length_choices = {k: v for k, v in moves.items() if v['seq_length'] == max_length}

            # Then select by highest number of possible ship alignments.
            max_fit_pos = max(length_choices, key=lambda x: length_choices[x]['possible_alignments'])
            max_fit = length_choices[max_fit_pos]['possible_alignments']
            choices = [move for move in length_choices if length_choices[move]['possible_alignments'] == max_fit]
            y, x = choice(choices)

        # If not, search for possible targets from the grid.
        else:
            moves = _possible_targets(opp_board, opp_ships)
            highest = max(moves, key=lambda x: moves[x])
            choices = [move for move in moves if moves[move] == moves[highest]]
            y, x = choice(choices)

        return board_info.translate_coord_to_move(y, x)

    # Call to deploy ships at the start of the game.
    def place_ships(self, game_state):
        ships = game_state['Ships']
        player_board = game_state['MyBoard']
        result = ship_deploy.randomly_space_ships(player_board, ships)

        # In case it is impossible to place the ships in a non-adjacent way.
        if result is None:
            return ship_deploy.deploy_randomly(ships,player_board)

        print("Found possible ship placement after", result[-1]['attempts'], 'attempts')

        return ship_deploy.format_ship_deployment(result)


# Get possible hits given the opponent's board and remaining ships.
def _possible_hits(opp_board, opp_ships):
    hit_options = ship_target.adjacent_to_hits(opp_board)
    for hit in hit_options:
        possible_ship_count = ship_target.possible_hit_ships(opp_board, opp_ships, hit, hit_options[hit])
        hit_options[hit]['possible_alignments'] = possible_ship_count
    return hit_options


# Look for possible targets based on alignment information.
def _possible_targets(opp_board, opp_ships):
    alignments = ship_target.possible_alignments(opp_board, opp_ships, reduce=True)
    # Get all non-zero possible alignments and their indices.
    targets = {(y, x): val for y, row in enumerate(alignments) for x, val in enumerate(row) if val > 0}
    return targets


# Deploys all the ships randomly on a board, so that none of them are adjacent.


# Try to place a ship in one of the available coordinates and then recurse and try with the next ship.


# Removes all neighbouring coordinates for a ship.


# Removes all neighbouring coordinates around a coordinate, as well as the coordinate itself.


# Variant of the ship deployment algorithm that checks the set of available coordinates, rather then the board.


# Format a dictionary of placements to fit the REST format.
