from random import choice
from random import shuffle
import numpy as np

import src.ai.ai_helpers as ai_help


class Bot:

    def __init__(self):
        self.bot_name = 'Pho'
        self.heuristics = []

    def set_heuristics(self, heuristics):
        self.heuristics = heuristics

    def make_move(self, game_state):
        opp_ships = np.array(ai_help.ships_still_afloat(game_state['Ships'], game_state['OppBoard']))
        opp_board = np.array(game_state['OppBoard'])

        # If there are hits, try nearby targets.
        if 'H' in opp_board:

            moves = self.possible_hits(opp_board, opp_ships)

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
            moves = self.possible_targets(opp_board, opp_ships)
            highest = max(moves, key=lambda x: moves[x])
            choices = [move for move in moves if moves[move] == moves[highest]]
            y, x = choice(choices)

        return ai_help.translate_coord_to_move(y, x)

    # Call to deploy ships at the start of the game.
    def place_ships(self, game_state):
        ships = game_state['Ships']
        player_board = game_state['MyBoard']
        result = randomly_space_ships(player_board, ships)

        # In case it is impossible to place the ships in a non-adjacent way.
        if result is None:
            return ai_help.deploy_randomly(game_state)

        print("Found possible ship placement after", result[-1]['attempts'], 'attempts')

        return format_ship_deployment(result)

    # Get possible hits given the opponent's board and remaining ships.
    def possible_hits(self, opp_board, opp_ships):
        hit_options = ai_help.adjacent_to_hits(opp_board)
        for hit in hit_options:
            possible_ship_count = ai_help.possible_hit_ships(opp_board, opp_ships, hit, hit_options[hit])
            hit_options[hit]['possible_alignments'] = possible_ship_count
        return hit_options

    # Look for possible targets based on alignment information.
    def possible_targets(self, opp_board, opp_ships):
        scores = ai_help.get_targeting_scores(opp_board, opp_ships, self.heuristics)
        # Get all non-zero possible alignments and their indices.
        targets = {(y, x): val for y, row in enumerate(scores) for x, val in enumerate(row)}
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

    shuffle(available_coords)
    available_coords = set(available_coords)

    # Search for a placement that spaces out the ships as as desired.
    if place_spaced_ship(available_coords, player_board, ships, placements, attempts):
        return placements

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
    shuffled_coords = list(available_coords)
    shuffle(shuffled_coords)

    for coord in shuffled_coords:
        y, x = coord

        # The directions are shuffled to avoid predictable alignments whenever it is easy to place ships.
        orientation = ['V', 'H']
        shuffle(orientation)
        for o in orientation:
            # Try to deploy the ship
            result = deploy_ship(coord, board, ship, o, ship_no, available_coords)
            attempts += 1
            if result:
                # If successful, append the positioning (avoids having to search for it later).
                placements.append(
                    {'position': coord, 'ship': ship, 'ship_no': ship_no, 'orientation': o, 'attempts': attempts})
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
def remove_neighbouring_coords(position, orientation, available_coords, ship, board):
    y, x = position

    if orientation == 'V':
        for i in range(y, y + ship):
            remove_neighbours((i, x), available_coords, board)
    if orientation == 'H':
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


# Variant of the ship deployment algorithm that checks the set of available coordinates, rather then the board.
def deploy_ship(coordinate, board, length, orientation, ship_num, available_coordinates):
    y, x = coordinate
    if orientation == "V":  # If we are trying to place ship vertically
        if y + length - 1 >= len(board):  # If ship doesn't fit within board boundaries
            return False  # Ship not deployed
        for i in range(length):  # For every section of the ship
            if (y + i, x) not in available_coordinates:  # If there is something on the board obstructing the ship
                return False  # Ship not deployed
        for i in range(length):  # For every section of the ship
            board[y + i][x] = str(ship_num)  # Place the ship on the board
    else:  # If we are trying to place ship horizontally
        if x + length - 1 >= len(board[0]):  # If ship doesn't fit within board boundaries
            return False  # Ship not deployed
        for j in range(length):  # For every section of the ship
            if (y, x + j) not in available_coordinates:  # If there is something on the board obstructing the ship
                return False  # Ship not deployed
        for j in range(length):  # For every section of the ship
            board[y][x + j] = str(ship_num)  # Place the ship on the board
    return True  # Ship deployed


# Format a dictionary of placements to fit the REST format.
def format_ship_deployment(placements):
    accepted_format = []
    ordered = sorted(placements, key=lambda x: x['ship_no'])
    for entry in ordered:
        y, x = entry['position']
        accepted_format.append(ai_help.translate_ship(y, x, entry['orientation']))

    accepted_format = {"Placement": accepted_format}
    return accepted_format

