import importlib
import os


class AI:

    def __init__(self):
        self.PLUGIN_PATH = 'src.ai.bots.' # this is lazy but writing it dynamically is too much of a pain right now.
        self.bot = None

    # Receive the name of a bot module to load from the 'bots' sub-folder.
    # Class name needs to be "Bot" to be found.
    def load_bot(self, name):
        location = self.PLUGIN_PATH + name
        self.bot = getattr(importlib.import_module(location), 'Bot')

    # Asks bot to either place its ships or start hunting based on game state.
    def make_decision(self, game_state):
        if game_state['Round'] == 0:
            self.bot.placeShips(self, game_state)
        else:
            self.bot.makeMove(self, game_state)


