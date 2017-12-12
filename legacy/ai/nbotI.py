from random import randint, choice
import json
import numpy as np   # Base N-dimensional array package
import bot_helpers as bot_help

#TODO adjust hitting to only bother with directions that make sense (e.g don't fire at positions where the ship cannot exist).
#TODO perform subset checks on alignments to remove irrelevant choices entirely (useful when going probabilistic).
#TODO rearrange so as to fit any number of bots.
class NbotI:

    def __init__(self):
        self.bot_name ='NbotI'

    def makeMove(self):
        opp_ships = np.array(bot_help.shipsStillAfloat(gameState))
        opp_board = np.array(gameState['OppBoard'])

        #If there are hits, try nearby targets.
        if 'H' in opp_board:
            moves = possible_hits(opp_board,opp_ships)
            highest = max(moves, key=lambda x:moves[x])
            choices = [move for move in moves if moves[move] == moves[highest]]
            y,x = choice(choices)

        #If not, find possible targets from the grid.
        else:
            moves = possible_targets(opp_board, opp_ships)
            highest = max(moves, key=lambda x:moves[x])
            choices = [move for move in moves if moves[move] == moves[highest]]
            print('Targeting...')
            print('choices:',choices)

            y,x = choice(choices)

        print("Firing at:",translateMove(y,x))
        return translateMove(y,x)


    #Call to deploy ships at the start of the game.
    def placeShips(self, gameState):
        return bot_help.deployRandomly(gameState)


def possible_hits(opp_board, opp_ships):
    hit_options = adjacent_to_hits(opp_board, opp_ships)
    for hit in hit_options:

#Find locations adjacent to possible hits and records their lengths.
def adjacent_to_hits(opp_board, opp_ships):
    hits = {}
    vert_visited = np.zeros((len(opp_board),len(opp_board[0])), dtype=bool)
    horz_visited = np.zeros((len(opp_board),len(opp_board[0])), dtype=bool)
    for (y,x),val in np.ndenumerate(opp_board):
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
                    add_to_hits(hits, top, vert_length,'top')
                if bottom:
                    add_to_hits(hits, bottom, vert_length,'bottom')

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
                    add_to_hits(hits, left, horz_length,'left')
                if right:
                    add_to_hits(hits, right, horz_length,'right')

    return hits

#Helper method for adding hits. If multiple ship lengths intersect, it will
#prioritise the larger one. Normally this should never happen if the AI greedily
#hunts down the longest found ship before bothering with another one.
def add_to_hits(hits,coord,seqLength,direction):
    if coord not in hits:
        hits[coord] = {'seqLength':seqLength,'direction':direction}
    elif seqLength > hits[coord]['seqLength']:
        print("Why is this executing?!")
        hits[coord] = {'seqLength':seqLength,'direction':direction}

#Go through each valid tile and attempt a shot. Observe how much this reduces possible
#alignments and return each move.
def possible_targets(opp_board, opp_ships):
    alignments = ai_help.possible_alignments(opp_board, opp_ships)
    #Get all non-zero possible alignements and their indices.
    targets = {(y,x):val for y,row in enumerate(alignments) for x,val  in enumerate(row) if val > 0}
    return targets


#Helper methods to put variables into a dictionary.
def make_target(y,x,alignment):
    return {'y':y,'x':x,'alignment':alignment}
