#   ____        _   _   _           _     _
#  | __ )  __ _| |_| |_| | ___  ___| |__ (_)_ __  ___
#  |  _ \ / _` | __| __| |/ _ \/ __| '_ \| | '_ \/ __|
#  | |_) | (_| | |_| |_| |  __/\__ \ | | | | |_) \__ \
#  |____/ \__,_|\__|\__|_|\___||___/_| |_|_| .__/|___/
#                                          |_|
#
botName='Nbot'

from random import randint, choice
from collections import namedtuple

import json

# These are the only additional libraries available to you. Uncomment them
# to use them in your solution.
#
import numpy as np   # Base N-dimensional array package
#import pandas   # Data structures & analysis

#Structs that contain info & heuristic values to choose next move.

#TODO enhance hits with impact on alignment
#TODO get more info on different move options.
def calculateMove(gameState):
    oppShips = shipsStillAfloat(gameState)
    oppBoard = np.array(gameState['OppBoard'])
    #If there are hits, try nearby targets.
    if 'H' in oppBoard:
        moves = possibleHits(oppBoard,oppShips)
        sorted_moves = sorted(moves, key=lambda x:x.hitLength)
        choice = sorted_moves[0]
    #If not, find possible targets from the grid.
    else:
        moves = possibleTargets(oppBoard, oppShips)
        sorted_align = sorted(moves, key=lambda x:x.alignments)
        sorted_impact = sorted(moves, key=lambda x:x.impact)
        choice = sorted_impact[0]

    return translateMove(y,x)

#Find locations adjacent to possible hits and give preference to
#long hit sequences.
def possibleHits(oppBoard, oppShips):
    hits = []
    vertVisited = np.zeros(oppBoard.shape, dtype=bool)
    horiVisited = np.zeros(oppBoard.shape, dtype=bool)
    for (y,x) in np.ndenumerate(oppBoard):
        if oppBoard[y,x] == 'H':
            #Search vertically
            if not vertVisited[y,x]:
                vertVisited[y,x] = True
                vertLength = 1
                top = bottom = None

                #Search above
                for i in range(1,y):
                    if oppBoard[y-i,x] == 'H':
                        vertVisited[y-i,x] = True
                        vertLength += 1
                    else:
                        top = (y-i,x)
                        break

                #Search below
                for i in range(1,oppBoard.shape[0]-y):
                    if oppBoard[y+i,x] == 'H':
                        vertVisited[y+i,x] = True
                        vertLength += 1
                    else:
                        bottom = (y+i,x)
                        break

                if top:
                    hits.append(makeHit(top[0],top[1],vertLength))
                if bottom:
                    hits.append(makeHit(bottom[0],bottom[1],vertLength))

            #Search horizontally
            if not horzVisited[y,x]:
                horzVisited[y,x] = True
                horzLength = 1
                left = right = None

                #Search left
                for j in range(1,x):
                    if oppBoard[y,x-j] == 'H':
                        horzLength[y,x-j] = True
                        horzLength += 1
                    else:
                        left = (y,x-j)
                        break

                #Search right
                for i in range(1,oppBoard.shape[0]-y):
                    if oppBoard[y,x+j] == 'H':
                        horzVisited[y,x+j] = True
                        horzLength += 1
                    else:
                        right = (y,x+j)
                        break

                if left:
                    hits.append(makeHit(left[0],left[1],horzLength))
                if right:
                    hits.append(makeHit(right[0],right[1],horzLength))

    return hits

#Go through each valid tile and attempt a shot. Observe how much this reduces possible
#alignments and return each move.
def possibleTargets(oppBoard, oppShips):
    defAlignment, totalAlignments = possibleAlignments(oppBoard, oppShips)

    #Get all non-zero possible alignements and their indices.
    targets = [makeTarget(y,x,val,0) for y,row in enumerate(defAlignment) for x,val  in enumerate(row) if val > 0]

    #Try shooting at a coordinate to see how much it reduces the total alignments.
    for target in targets:
        oppBoard[target['y']][target['x']] = 'T'
        target['impact'] = totalAlignments - possibleAlignments(oppBoard, oppShips)[1]
        oppBoard[target['y']][target['x']] = ''

    return targets

#For each cell, calculate the number of possible alignments and return the results + possibilities.
def possibleAlignments(oppBoard, oppShips):
    alignments = np.zeros((len(oppBoard),len(oppBoard[0])), dtype=int)
    #y is the row, x is the column
    for y in range(0,len(oppBoard)):
        for x in range(0,len(oppBoard[0])):
            if oppBoard[y][x] == '':
                alignments[y,x] = alignmentsIn(y,x, oppBoard, oppShips)

    return (alignments, np.sum(alignments))

#Gets number of valid alignments for a position
def alignmentsIn(y,x, oppBoard, oppShips):
    validAlignments = 0
    for shipLength in oppShips:
        for i in range(0,shipLength):
            #Vertical alignment attempts
            if y-i >= 0 and canDeploy(y-i,x, oppBoard, shipLength, "V"):
                validAlignments +=1
            #Horizontal alignment attempts
            if x-i >= 0 and canDeploy(y,x-i, oppBoard, shipLength,"H"):
                validAlignments += 1

    return validAlignments

#Ascertains if a given ship can be deployed at a given location
def canDeploy(i,j,board, length, orientation):
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
def makeTarget(y,x,alignment,impact):
    return {'y':y,'x':x,'alignment':alignment,'impact':impact}

def makeHit(y,x,seqLength):
    return {'y':y,'x':x,'seqLength':seqLength}

# =============================================================================
# The code below shows a selection of helper functions designed to make the
# time to understand the environment and to get a game running as short as
# possible. The code also serves as an example of how to manipulate the myBoard
# and oppBoard dictionaries that are in gameState.

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

# Randomly guesses a location on the board that hasn't already been hit
def chooseRandomValidTarget(gamestate):
    valid = False
    row = None
    column = None
    while not valid:  # Keep randomly choosing targets until a valid one is chosen
        row = randint(0, len(gamestate["MyBoard"]) - 1)  # Randomly pick a row
        column = randint(0, len(gamestate["MyBoard"][0]) - 1)  # Randomly pick a column
        if gamestate["OppBoard"][row][column] == "":  # If the target is sea that hasn't already been guessed...
            valid = True  # ...then the target is valid
    move = {"Row": chr(row + 65),
            "Column": (column + 1)}  # Set move equal to the valid target (convert the row to a letter 0->A, 1->B etc.)
    return move  # Return the move


# Returns a list of the lengths of your opponent's ships that haven't been sunk
def shipsStillAfloat(gamestate):
    afloat = []
    ships_removed = []
    for k in range(len(gamestate["Ships"])):  # For every ship
        afloat.append(gamestate["Ships"][k])  # Add it to the list of afloat ships
        ships_removed.append(False)  # Set its removed from afloat list to false
    for i in range(len(gamestate["OppBoard"])):
        for j in range(len(gamestate["OppBoard"][0])):  # For every grid on the board
            for k in range(len(gamestate["Ships"])):  # For every ship
                if str(k) in gamestate["OppBoard"][i][j] and not ships_removed[k]:  # If we can see the ship number on our opponent's board and we haven't already removed it from the afloat list
                    afloat.remove(gamestate["Ships"][k])  # Remove that ship from the afloat list (we can only see an opponent's ship number when the ship has been sunk)
                    ships_removed[k] = True  # Record that we have now removed this ship so we know not to try and remove it again
    return afloat  # Return the list of ships still afloat


# Returns a list of cells adjacent to the input cell that are free to be targeted (not including land)
def selectUntargetedAdjacentCell(row, column, oppBoard):
    adjacent = []  # List of adjacent cells
    if row > 0 and oppBoard[row - 1][column] == "":  # If there is a cell above
        adjacent.append((row - 1, column))  # Add to list of adjacent cells
    if row < len(oppBoard) - 1 and oppBoard[row + 1][column] == "":  # If there is a cell below
        adjacent.append((row + 1, column))  # Add to list of adjacent cells
    if column > 0 and oppBoard[row][column - 1] == "":  # If there is a cell left
        adjacent.append((row, column - 1))  # Add to list of adjacent cells
    if column < len(oppBoard[0]) - 1 and oppBoard[row][column + 1] == "":  # If there is a cell right
        adjacent.append((row, column + 1))  # Add to list of adjacent cells
    return adjacent


# Given a valid coordinate on the board returns it as a correctly formatted move
def translateMove(row, column):
    return {"Row": chr(row + 65), "Column": (column + 1)}
