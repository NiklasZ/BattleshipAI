import fileIO as io
import datetime

#Class that exists to log games the bots partake in.
class GameRecorder:
    def __init__ (self, game_state, bot_name):
        self.bot_name = bot_name #Name of our bot.
        self.opponentId = game_state['OpponentId'] #Name of opponent's bot.
        self.gameId = game_state['GameId'] #ID of the game.

        #Initial setup.
        self.save_path = io.create_dirs_for_bots(self.bot_name,self.opponentId )
        self.log.append(datetime.datetime.now().strftime('%d/%m/%y %H:%M:%S'))
        self.log.append('GameId: '+self.gameId )
        self.log.append('Ships: '+game_state['Ships'])
        self.log.append('--GAME START--\n\n'])

    #Record both boards every turn.
    def record_turn(self, game_state):
        self.log('\n')
        self.log(self.bot_name)
        self.log('\n'+self.board_to_string(game_state['MyBoard'])+'\n')
        self.log(self.opponent_name)
        self.log('\n'+self.board_to_string(game_state['OppBoard'])+'\n')
        self.log('\n')

    #Wrap up and write the file.
    def record_end(self,result):
        self.log('\nGame has ended: '+result)
        io.write_to_file(self.log, self.save_path+'/'+self.gameId)

    #Converts board to somewhat more readable string.
    def board_to_string(self, board):
        text = ''
        for row in board:
            for field in board:
                text += "{:<2}".format(field)+" "
            text += '\n'
