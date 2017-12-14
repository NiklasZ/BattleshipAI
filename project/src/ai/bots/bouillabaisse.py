from random import choice
import numpy as np  # Base N-dimensional array package
import src.ai.ai_helpers as ai_help

# TODO adjust hitting to only bother with directions that make sense (e.g don't fire at positions where the ship cannot exist).
# TODO perform subset checks on alignments to remove irrelevant choices entirely (useful when going probabilistic).
# TODO rearrange so as to fit any number of bots.
from src.ai.ai_helpers import adjacent_to_hits


class Bot:

    def __init__(self):
        self.bot_name = 'NbotI'

    def make_move(self):
        opp_ships = np.array(ai_help.ships_still_afloat(gameState))
        opp_board = np.array(gameState['OppBoard'])

        # If there are hits, try nearby targets.
        if 'H' in opp_board:
            moves = possible_hits(opp_board, opp_ships)
            highest = max(moves, key=lambda x: moves[x])
            choices = [move for move in moves if moves[move] == moves[highest]]
            y, x = choice(choices)

        # If not, find possible targets from the grid.
        else:
            moves = possible_targets(opp_board, opp_ships)
            highest = max(moves, key=lambda x: moves[x])
            choices = [move for move in moves if moves[move] == moves[highest]]
            print('Targeting...')
            print('choices:', choices)

            y, x = choice(choices)

        print("Firing at:", translateMove(y, x))
        return translateMove(y, x)

    # Call to deploy ships at the start of the game.
    def place_ships(self, gameState):
        return ai_help.deployRandomly(gameState)


def possible_hits(opp_board, opp_ships):
    hit_options = adjacent_to_hits(opp_board, opp_ships)
    for hit in hit_options:
        possible_ship_count = ai_help.possible_hit_ships(opp_board, opp_ships, hit, hit_options[hit])
        hit_options[hit]['possible_ships'] = possible_ship_count

    return hit_options


# Look for possible targets based on alignment information.
def possible_targets(opp_board, opp_ships):
    alignments = ai_help.possible_alignments(opp_board, opp_ships)
    # Get all non-zero possible alignements and their indices.
    targets = {(y, x): val for y, row in enumerate(alignments) for x, val in enumerate(row) if val > 0}
    return targets
