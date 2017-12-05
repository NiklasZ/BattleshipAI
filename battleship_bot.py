#   ____        _   _   _           _     _
#  | __ )  __ _| |_| |_| | ___  ___| |__ (_)_ __  ___
#  |  _ \ / _` | __| __| |/ _ \/ __| '_ \| | '_ \/ __|
#  | |_) | (_| | |_| |_| |  __/\__ \ | | | | |_) \__ \
#  |____/ \__,_|\__|\__|_|\___||___/_| |_|_| .__/|___/
#                                          |_|
#
botName='NbotI'

from random import randint, choice
from collections import namedtuple

import json

import numpy as np   # Base N-dimensional array package
#import pandas   # Data structures & analysis

#Structs that contain info & heuristic values to choose next move.

#TODO remove impact (has no effect)
#TODO adjust hitting to only bother with directions that make sense (e.g don't fire at positions where the ship cannot exist).
#TODO perform subset checks on alignments to remove irrelevant choices entirely (useful when going probabilistic)-
def calculateMove(gameState):

    gameState['opp_board'] = gameState['OppBoard']

    opp_ships = shipsStillAfloat(gameState)
    opp_board = np.array(gameState['opp_board'])

    #Deploy ships at start of game.
    if gameState['Round'] == 0:
        return deployRandomly(gameState)


    #If there are hits, try nearby targets.
    if 'H' in opp_board:
        moves = possible_hits(opp_board,opp_ships)
        highest = max(moves, key=lambda x:moves[x])
        choices = [move for move in moves if moves[move] == moves[highest]]
        y,x = choice(choices)

    #If not, find possible targets from the grid.
    else:
        moves = possible_targets(opp_board, opp_ships)
        align_highest = max(moves, key=lambda x:x['alignment'])['alignment']
        impact_highest = max(moves, key=lambda x:x['impact'])['impact']

        align_choices = [move for move in moves if move['alignment'] == align_highest]
        impact_choices = [move for move in moves if move['impact'] == impact_highest]

        print('Targeting...')
        print('choices:',impact_choices)
        if(impact_choices != impact_choices):
            print('align recommends different choice:',align_choices)
        coord = choice(impact_choices)
        y = coord['y']
        x = coord['x']

    print("Firing at:",(y,x))
    print("Position on board:",translateMove(y,x))
    return translateMove(y,x)

#Find locations adjacent to possible hits and give preference to
#long hit sequences.
def possible_hits(opp_board, opp_ships):
    hits = {}
    vert_visited = np.zeros((len(opp_board),len(opp_board[0])), dtype=bool)
    horz_visited = np.zeros((len(opp_board),len(opp_board[0])), dtype=bool)
    for idx,val in np.ndenumerate(opp_board):
        y = idx[0]
        x = idx[1]
        if opp_board[y][x] == 'H':
            #Search vertically
            if not vert_visited[y,x]:
                vert_visited[y,x] = True
                vert_length = 1
                top = bottom = None

                #Search above
                i=1
                while(y-i >= 0):
                    if opp_board[y-i][x] == 'H':
                        vert_visited[y-i,x] = True
                        vert_length += 1
                    else:
                        if opp_board[y-i][x] == '':
                            top = (y-i,x)
                        break
                    i+=1

                #Search below
                i=1
                while(y+i < len(opp_board)):
                    if opp_board[y+i][x] == 'H':
                        vert_visited[y+i,x] = True
                        vert_length += 1
                    else:
                        if opp_board[y+i][x] == '':
                            bottom = (y+i,x)
                        break
                    i+=1

                if top:
                    add_to_hits(hits, top, vert_length)
                if bottom:
                    add_to_hits(hits, bottom, vert_length)

            #Search horizontally
            if not horz_visited[y,x]:
                horz_visited[y,x] = True
                horz_length = 1
                left = right = None

                #Search left
                j=1
                while(x-j >= 0):
                    if opp_board[y][x-j] == 'H':
                        horz_length[y,x-j] = True
                        horz_length += 1
                    else:
                        if opp_board[y][x-j] == '':
                            left = (y,x-j)
                        break
                    j+=1

                #Search right
                j=1
                while(x+j < len(opp_board[0])):
                    if opp_board[y][x+j] == 'H':
                        horz_visited[y,x+j] = True
                        horz_length += 1
                    else:
                        if opp_board[y][x+j] == '':
                            right = (y,x+j)
                        break
                    j+=1

                if left:
                    add_to_hits(hits, left, horz_length)
                if right:
                    add_to_hits(hits, right, horz_length)

    return hits

#Helper method for adding hits. Aggregates points where multiple Hs meet.
def add_to_hits(hits,coord,seqLength):
    if coord not in hits:
        hits[coord] = seqLength
    else:
        hits[coord] += seqLength

#Go through each valid tile and attempt a shot. Observe how much this reduces possible
#alignments and return each move.
def possible_targets(opp_board, opp_ships):
    def_alignment, total_alignments = possible_alignments(opp_board, opp_ships)

    #Get all non-zero possible alignements and their indices.
    targets = [make_target(y,x,val,0) for y,row in enumerate(def_alignment) for x,val  in enumerate(row) if val > 0]

    #Try shooting at a coordinate to see how much it reduces the total alignments.
    for target in targets:
        opp_board[target['y']][target['x']] = 'T'
        target['impact'] = total_alignments - possible_alignments(opp_board, opp_ships)[1]
        opp_board[target['y']][target['x']] = ''

    return targets

#For each cell, calculate the number of possible alignments and return the results + possibilities.
def possible_alignments(opp_board, opp_ships):
    alignments = np.zeros((len(opp_board),len(opp_board[0])), dtype=int)
    #y is the row, x is the column
    for y in range(0,len(opp_board)):
        for x in range(0,len(opp_board[0])):
            if opp_board[y][x] == '':
                alignments[y,x] = alignments_in(y,x, opp_board, opp_ships)

    return (alignments, np.sum(alignments))

#Gets number of valid alignments for a position
def alignments_in(y,x, opp_board, opp_ships):
    valid_alignments = 0
    for shipLength in opp_ships:
        for i in range(0,shipLength):
            #Vertical alignment attempts
            if y-i >= 0 and can_deploy(y-i,x, opp_board, shipLength, "V"):
                valid_alignments +=1
            #Horizontal alignment attempts
            if x-i >= 0 and can_deploy(y,x-i, opp_board, shipLength,"H"):
                valid_alignments += 1

    return valid_alignments

#Ascertains if a given ship can be deployed at a given location
def can_deploy(i,j,board, length, orientation):
    if orientation == "V":  # If we are trying to place ship vertically
        if i + length - 1 >= len(board):  # If ship doesn't fit within board boundaries
            return False  # Ship not deployed
        for l in range(length):  # For every section of the ship
            if board[i + l][j] != "":  # If there is something on the board obstructing the ship
                return False  # Ship not deployed
    else:  # If we are trying to place ship horizontally
        if j + length - 1 >= len(board[0]):  # If ship doesn't fit within board boundaries
            return False  # Ship not deployed
        for l in range(length):  # For every section of the ship
            if board[i][j + l] != "":  # If there is something on the board obstructing the ship
                return False  # Ship not deployed
    return True  # Ship fits

#Helper methods to put variables into a dictionary.
def make_target(y,x,alignment,impact):
    return {'y':y,'x':x,'alignment':alignment,'impact':impact}

# =============================================================================
# The code below shows a selection of helper functions designed to make the
# time to understand the environment and to get a game running as short as
# possible. The code also serves as an example of how to manipulate the myBoard
# and opp_board dictionaries that are in gameState.

# Deploys all the ships randomly on a blank board
def deployRandomly(gamestate):
    move = []  # Initialise move as an emtpy list
    orientation = None
    row = None
    column = None
    for i in range(len(gamestate["Ships"])):  # For every ship that needs to be deployed
        deployed = False
        while not deployed:  # Keep randomly choosing locations until a valid one is chosen
            row = randint(0, len(gamestate["MyBoard"]) - 1)  # Randomly pick a row
            column = randint(0, len(gamestate["MyBoard"][0]) - 1)  # Randomly pick a column
            orientation = choice(["H", "V"])  # Randomly pick an orientation
            if deployShip(row, column, gamestate["MyBoard"], gamestate["Ships"][i], orientation, i):  # If ship can be successfully deployed to that location...
                deployed = True  # ...then the ship has been deployed
        move.append({"Row": chr(row + 65), "Column": (column + 1),
                     "Orientation": orientation})  # Add the valid deployment location to the list of deployment locations in move
    return {"Placement": move}  # Return the move


# Returns whether given location can fit given ship onto given board and, if it can, updates the given board with that ships position
def deployShip(i, j, board, length, orientation, ship_num):
    if orientation == "V":  # If we are trying to place ship vertically
        if i + length - 1 >= len(board):  # If ship doesn't fit within board boundaries
            return False  # Ship not deployed
        for l in range(length):  # For every section of the ship
            if board[i + l][j] != "":  # If there is something on the board obstructing the ship
                return False  # Ship not deployed
        for l in range(length):  # For every section of the ship
            board[i + l][j] = str(ship_num)  # Place the ship on the board
    else:  # If we are trying to place ship horizontally
        if j + length - 1 >= len(board[0]):  # If ship doesn't fit within board boundaries
            return False  # Ship not deployed
        for l in range(length):  # For every section of the ship
            if board[i][j + l] != "":  # If there is something on the board obstructing the ship
                return False  # Ship not deployed
        for l in range(length):  # For every section of the ship
            board[i][j + l] = str(ship_num)  # Place the ship on the board
    return True  # Ship deployed

# Returns a list of the lengths of your opponent's ships that haven't been sunk
def shipsStillAfloat(gamestate):
    afloat = []
    ships_removed = []
    for k in range(len(gamestate["Ships"])):  # For every ship
        afloat.append(gamestate["Ships"][k])  # Add it to the list of afloat ships
        ships_removed.append(False)  # Set its removed from afloat list to false
    for i in range(len(gamestate["opp_board"])):
        for j in range(len(gamestate["opp_board"][0])):  # For every grid on the board
            for k in range(len(gamestate["Ships"])):  # For every ship
                if str(k) in gamestate["opp_board"][i][j] and not ships_removed[k]:  # If we can see the ship number on our opponent's board and we haven't already removed it from the afloat list
                    afloat.remove(gamestate["Ships"][k])  # Remove that ship from the afloat list (we can only see an opponent's ship number when the ship has been sunk)
                    ships_removed[k] = True  # Record that we have now removed this ship so we know not to try and remove it again
    return afloat  # Return the list of ships still afloat


# Given a valid coordinate on the board returns it as a correctly formatted move
def translateMove(row, column):
    return {"Row": chr(row + 65), "Column": (column + 1)}
