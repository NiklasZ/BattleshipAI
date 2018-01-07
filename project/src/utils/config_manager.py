import src.ai.ai
import src.ai.ai as ai
import src.ai.heuristics as heur
import src.ai.bot_learning as learn
import src.utils.game_recorder as record
import src.ai.offensive_explorer as explore

import configparser

config = configparser.ConfigParser(allow_no_value=True)
config.read('settings.ini')

ai_config = config['AI']
ai.PLUGIN_PATH = ai_config['bot plugin path']


heur_config = config['Heuristics']
heur.SEARCH_RANGES['ship_adjacency'] = [float(i) for i in heur_config['ship adjacency value box'].split(',')]

train_config = config['Training']
ai.TRAIN_INTERVAL = int(train_config['bot training frequency'])
ai.GAME_COUNT = int(train_config['games to train'])
ai.UNDERPERFOMANCE_THRESHOLD = float(train_config['force training if bot underperforms by'])
ai.MAX_GAMES_WITHOUT_TRAINING = int(train_config['max games without training'])

learn_config = config['Optimisation']
learn.BB_GLOBAL_CALLS = int(learn_config['black box global calls'])
learn.BB_LOCAL_CALLS = int(learn_config['black box local calls'])
learn.PARALLEL_CALLS = int(learn_config['parallel calls'])
explore.BOARD_SAMPLES = int(learn_config['boards to sample per game'])

record_config = config['Logging']
record.MAX_GAMES_LOGGED_PER_OPPONENT = int(record_config['max games to log per opponent'])