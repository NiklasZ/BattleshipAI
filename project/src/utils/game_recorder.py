import src.utils.fileIO as io
import datetime


# Class that exists to log games the bots partake in.
class GameRecorder:
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
        self.log = [datetime.datetime.now().strftime('%d/%m/%y %H:%M:%S')]
        self.log.append('\nGameId: ' + str(self.game_id))
        self.log.append('\nShips: ' + str(game_state['Ships']))
        self.log.append('\n--GAME START--\n\n')

    # Record both boards every turn.
    def record_turn(self, game_state):
        self.game_states.append(game_state)

        self.log.append('\n')
        self.log.append(self.bot_name)
        self.log.append('\n' + self.board_to_string(game_state['MyBoard']) + '\n')
        self.log.append(self.opponent_name)
        self.log.append('\n' + self.board_to_string(game_state['OppBoard']) + '\n')
        self.log.append('\n')

    # Wrap up and write the file.
    def record_end(self):
        self.log.append('\n\n--GAME END--')
        self.game_history[self.game_id] = self.game_states
        io.save_game_log(self.bot_name, self.opponent_name, self.game_id, ''.join(self.log), self.game_history)

    # Converts board to somewhat more readable string.
    def board_to_string(self, board):
        text = ''
        for row in board:
            for field in row:
                text += "{:<2}".format(field) + " "
            text += '\n'

        return text
