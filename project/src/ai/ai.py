import importlib
import os


class AI:

    def __init__(self):
        #TODO make this dynamic rather than fixed.
        self.PLUGIN_PATH = 'src.ai.bots.' # this is lazy but writing it dynamically is too much of a pain right now.
        self.bot = None

    # Receive the name of a bot module to load from the 'bots' sub-folder.
    # Class name needs to be "Bot" to be found.
    def load_bot(self, name):
        location = self.PLUGIN_PATH + name
        self.bot = getattr(importlib.import_module(location), 'Bot')() #Gets the class Bot and creates an instance of it.
        print("Loading bot:", self.bot.bot_name)

    # Asks bot to either place its ships or start hunting based on game state.
    def make_decision(self, game_state):
        if game_state['Round'] == 0:
            return self.bot.place_ships(game_state)
        else:
            return self.bot.make_move(game_state)


