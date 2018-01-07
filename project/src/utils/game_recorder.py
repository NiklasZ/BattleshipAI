# This module records games either as textual logs or pickles them for later use.
# project imports
import src.utils.file_io as io

# library imports
import datetime


MAX_GAMES_LOGGED_PER_OPPONENT = 200 # The largest number of games to log in a pickle file.
LOG_TEXT = False # Whether to also log the games in files as text. This generates a log file per game.

# Class that exists to log games the bots partake in.
class GameRecorder:
    """
    A recorder class that can be fed game states to log and write to a file oncce the game is complete.
    """
    def __init__(self, game_state, bot_name):
        self.bot_name = bot_name  # Name of our bot.
        self.opponent_name = game_state['OpponentId']  # Name of opponent's bot.
        self.game_id = game_state['GameId']  # ID of the game.
        self.game_history = io.load_pickled_game_log(self.bot_name, self.opponent_name)
        if not self.game_history:
            self.game_history = {}
        self.game_states = [game_state]

        # Initial setup.
        io.create_dirs(self.bot_name, self.opponent_name)

    # Record both boards every turn.
    def record_turn(self, game_state):
        self.game_states.append(game_state)


    # Wrap up and write the file.
    def record_end(self):
        self.game_history[self.game_id] = self.game_states
        if len(self.game_history) > MAX_GAMES_LOGGED_PER_OPPONENT:
            self.game_history = {k:self.game_history[k] for k in sorted(self.game_history, reverse=True)[:MAX_GAMES_LOGGED_PER_OPPONENT]}

        io.save_pickled_game_log(self.bot_name,self.opponent_name,self.game_history)

        if LOG_TEXT:
            write_log_as_text(self.bot_name,self.game_states)


def write_log_as_text(bot_name,game_states):

    game_id = game_states[0]['GameId']
    opponent_name = game_states[0]['OpponentId']

    log = [datetime.datetime.now().strftime('%d/%m/%y %H:%M:%S')]
    log.append('\nGameId: ' + str(game_id))
    log.append('\nShips: ' + str(game_states[0]['Ships']))
    log.append('\n--GAME START--\n\n')

    for game_state in game_states:
        log.append('\n')
        log.append(bot_name)
        log.append('\n' + board_to_string(game_state['MyBoard']) + '\n')
        log.append(opponent_name)
        log.append('\n' + board_to_string(game_state['OppBoard']) + '\n')
        log.append('\n')

    log.append('\n\n--GAME END--')
    io.save_textual_game_log(bot_name, opponent_name, game_id, ''.join(log))


 # Converts board to somewhat more readable string.
def board_to_string(board):
    text = ''
    for row in board:
        for field in row:
            text += "{:<2}".format(field) + " "
        text += '\n'

    return text
