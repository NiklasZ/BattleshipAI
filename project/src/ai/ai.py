import importlib
import os


class AI:

    def __init__(self):
        self.PLUGIN_PATH = 'bots.'

    # Receive the name of a bot module to load.
    # Class name needs to be "Bot" to be found.
    def load_bot(self, name):
        location = self.PLUGIN_PATH+name
        bot_class = getattr(importlib.import_module(location), 'Bot')

