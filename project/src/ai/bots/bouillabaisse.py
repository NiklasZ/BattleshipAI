from random import choice
import numpy as np  # Base N-dimensional array package
import src.ai.ai_helpers as ai_help

from src.ai.ai_helpers import adjacent_to_hits, deploy_ship

# The Bouillabaisse bot is the the 1st completed bot.
# It uses mostly deterministic methods to choose targets.
# Simultaneously its ship placement is completely random.
class Bot:

    def __init__(self, opponent_profile):
        self.bot_name = 'Bouillabaisse'
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
    def place_ships(self, gameState):
        return deploy_randomly(gameState)


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

# Deploys all the ships randomly on a blank board
def deploy_randomly(game_state):
    move = []  # Initialise move as an emtpy list
    orientation = None
    row = None
    column = None
    for i in range(len(game_state["Ships"])):  # For every ship that needs to be deployed
        deployed = False
        while not deployed:  # Keep randomly choosing locations until a valid one is chosen
            row = np.random.randint(0, len(game_state["MyBoard"]) - 1)  # Randomly pick a row
            column = np.random.randint(0, len(game_state["MyBoard"][0]) - 1)  # Randomly pick a column
            orientation = np.random.choice(["H", "V"])  # Randomly pick an orientation
            if deploy_ship(row, column, game_state["MyBoard"], game_state["Ships"][i], orientation,
                           i):  # If ship can be successfully deployed to that location...
                deployed = True  # ...then the ship has been deployed
        move.append({"Row": chr(row + 65), "Column": (column + 1),
                     "Orientation": orientation})  # Add the valid deployment location to the list of deployment locations in move
    return {"Placement": move}  # Return the move