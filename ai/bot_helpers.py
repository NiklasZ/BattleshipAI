# =============================================================================
# The code below shows a selection of helper functions designed to make the
# time to understand the environment and to get a game running as short as
# possible. The code also serves as an example of how to manipulate the myBoard
# and opp_board dictionaries that are in gameState.

#For a hit option, calculate the number of possible alignments and return the results + possibilities.
def possible_hit_ships(opp_board, opp_ships, hit_option):
    #Remove ships that are too short to be possible.
    possible_ships = opp_ships - hit_options['seqLength']
    possible_ships[possible_ships > 0]
    ship_fits = 0

    #Based on the sequence's position, ascertain if there is enough room.
    #This works by trying to deploy a ship such that it ls positioned where the
    #known sequence is.
    if hit_option['direction'] == 'top':
        for ship_length in possible_ships:
            start_idx = hit_option[0] - ship_length
            if start_idx >= 0 and can_deploy(start_idx, hit_option[1], opp_board,ship_length, 'V'):
                ship_fits += 1

    if hit_option['direction'] == 'bottom':
        for ship_length in possible_ships:
            start_idx = hit_option[0] + ship_length
            if start_idx < len(opp_board) 0 and can_deploy(start_idx, hit_option[1], opp_board,ship_length, 'V'):
                ship_fits += 1

    if hit_option['direction'] == 'left':
        for ship_length in possible_ships:
            start_idx = hit_option[1] - ship_length
            if start_idx >= 0 and can_deploy(hit_option[0], start_idx, opp_board,ship_length, 'V'):
                ship_fits += 1
                
    if hit_option['direction'] == 'top':
        return alignments_in(hit_option[0],hit_option[1],opp_board,possible_ships)

def is_there_ship_space(opp_board, opp_ships, ):

def possible_alignments(opp_board, opp_ships):
    alignments = np.zeros((len(opp_board),len(opp_board[0])), dtype=int)
    #y is the row, x is the column
    for y in range(0,len(opp_board)):
        for x in range(0,len(opp_board[0])):
            if opp_board[y][x] == '':
                alignments[y,x] = alignments_in(y,x, opp_board, opp_ships)

    return alignments

#Gets number of valid alignments for a position
def alignments_in(y,x, opp_board, opp_ships):
    valid_alignments = 0
    for shipLength in opp_ships:
        for i in range(0,shipLength):
            #Vertical alignment attempts
            if y-i >= 0 and bot_help.can_deploy(y-i,x, opp_board, shipLength, "V"):
                valid_alignments +=1
            #Horizontal alignment attempts
            if x-i >= 0 and bot_help.can_deploy(y,x-i, opp_board, shipLength,"H"):
                valid_alignments += 1

    return valid_alignments

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

# Given a valid coordinate on the board returns it as a correctly formatted move
def translateMove(row, column):
    return {"Row": chr(row + 65), "Column": (column + 1)}
