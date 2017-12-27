import src.ai.ai as ai
import src.ai.heuristics as heur
import src.ai.bot_learning as learn
import src.utils.game_recorder as record

import configparser

config = configparser.ConfigParser(allow_no_value=True)
config.read('settings.ini')

ai_config = config['AI']
ai.PLUGIN_PATH = ai_config['bot plugin path']
ai.TRAIN_INTERVAL = int(ai_config['bot training frequency'])
ai.TRAINING_MAP_RATE = float(ai_config['map rate to choose type'])

heur_config = config['Heuristics']
heur.SEARCH_RANGES['ship_adjacency'] = [float(i) for i in heur_config['ship adjacency value box'].split(',')]

learn_config = config['Optimisation']
learn.BB_GLOBAL_CALLS = int(learn_config['black box global calls'])
learn.BB_LOCAL_CALLS = int(learn_config['black box local calls'])
learn.GAME_COUNT = int(learn_config['games to train'])
learn.REPLAYS = int(learn_config['replayable games'])
learn.PARALLEL_CALLS = int(learn_config['parallel calls'])

record_config = config['Logging']
record.MAX_GAMES_LOGGED_PER_OPPONENT = int(record_config['max games to log per opponent'])