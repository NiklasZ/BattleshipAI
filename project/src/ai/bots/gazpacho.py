from random import choice
from random import shuffle
import numpy as np  # Base N-dimensional array package
import src.ai.ai_helpers as ai_help

from src.ai.ai_helpers import adjacent_to_hits, deploy_ship


class Bot:

    def __init__(self, opponent_profile):
        self.bot_name = 'Gazpacho'
        self.opponent_profile = opponent_profile

    def make_move(self, game_state):
        opp_ships = np.array(ai_help.ships_still_afloat(game_state))
        opp_board = np.array(game_state['OppBoard'])

        # If there are hits, try nearby targets.
        if 'H' in opp_board:

            moves = possible_hits(opp_board, opp_ships)

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
            moves = possible_targets(opp_board, opp_ships)
            highest = max(moves, key=lambda x: moves[x])
            choices = [move for move in moves if moves[move] == moves[highest]]
            y, x = choice(choices)

        print("Firing at:", ai_help.translate_move(y, x))
        return ai_help.translate_move(y, x)

    # Call to deploy ships at the start of the game.
    def place_ships(self, game_state):
        ships = game_state['Ships']
        player_board = game_state['MyBoard']
        pass


# Get possible hits given the opponent's board and remaining ships.
def possible_hits(opp_board, opp_ships):
    hit_options = adjacent_to_hits(opp_board)
    for hit in hit_options:
        possible_ship_count = ai_help.possible_hit_ships(opp_board, opp_ships, hit, hit_options[hit])
        hit_options[hit]['possible_alignments'] = possible_ship_count
    return hit_options


# Look for possible targets based on alignment information.
def possible_targets(opp_board, opp_ships):
    alignments = ai_help.possible_alignments(opp_board, opp_ships)
    # Get all non-zero possible alignements and their indices.
    targets = {(y, x): val for y, row in enumerate(alignments) for x, val in enumerate(row) if val > 0}
    return targets


# Deploys all the ships randomly on a board, so that none of them are adjacent.
def randomly_space_ships(player_board, ships):
    available_coords = []
    placements = []
    attempts = 0
    # Find all available coordinates.
    for (y, x), val in np.ndenumerate(player_board):
        if val == '':
            available_coords.append((y, x))

    available_coords = set(shuffle(available_coords))

    # Search for a placement that spaces out the ships as as desired.
    if place_spaced_ship(available_coords, player_board, ships, placements, attempts):
        print("Found possible placement after", placements[-1]['attempts'], attempts)
        return player_board

    # In case there is no way to place the ships to be completely non-adjacent.
    return None

# Try to place a ship in one of the available coordinates and then recurse and try with the next ship.
def place_spaced_ship(available_coords, board, ships, placements, attempts):
    # If all ships have been placed, return.
    if len(ships) == 0:
        return True

    # Take a ship from the list and try to fit it.
    ship = ships.pop()
    ship_no = len(ships)

    # Go through each possible coordinate and alignment.
    for coord in available_coords:
        y, x = coord

        # The directions are shuffled to avoid predictable alignments whenever it is easy to place ships.
        orientation = ['V', 'H']
        for o in shuffle(orientation):
            # Try to deploy the ship
            result = ai_help.deploy_ship(y, x, board, ship, o, ship_no)
            attempts += 1
            if result:
                # If successful, append the positioning (avoids having to search for it later).
                placements.append(
                    {'position': coord, 'ship': ship, 'ship_no': ship_no, 'direction': 'V', 'attempts': attempts})
                # Copy the available coordinates and remove the used ones.
                new_available_coords = set(available_coords)
                remove_neighbouring_coords(coord, o, new_available_coords, ship, board)
                # Recurse and try the next ship.
                if place_spaced_ship(new_available_coords, board, ships, placements, attempts):
                    return True
                # If this proves unsuccessful, remove this ship placement and try again.
                else:
                    placements.pop()
                    ai_help.remove_ship(y, x, board, ship, o)

    # Re-attach the ship as the search was unsuccessful.
    ships.append(ship)

    # Not all ships have been placed and the permutations in this part are exhausted.
    return False

# Removes all neighbouring coordinates for a ship.
def remove_neighbouring_coords(position, direction, available_coords, ship, board):
    y, x = position

    if direction == 'V':
        for i in range(y, y + ship):
            remove_neighbours((i, x), available_coords, board)
    if direction == 'H':
        for j in range(x, x + ship):
            remove_neighbours((y, j), available_coords, board)

# Removes all neighbouring coordinates around a coordinate, as well as the coordinate itself.
def remove_neighbours(coordinate, available_coords, board):
    y, x = coordinate

    # Remove current position
    if (y, x) in available_coords:
        available_coords.remove((y, x))
    # Check above
    if y - 1 >= 0 and (y - 1, x) in available_coords:
        available_coords.remove((y - 1, x))
    # Check below
    if y + 1 < len(board) and (y + 1, x) in available_coords:
        available_coords.remove((y + 1, x))
        # Check left
    if x - 1 >= 0 and (y, x - 1) in available_coords:
        available_coords.remove((y, x - 1))
    # Check right
    if x + 1 < len(board[0]) and (y, x + 1) in available_coords:
        available_coords.remove((y, x + 1))

