import os
import pickle

DATA_DIR = '../data'
IMG_DIR = '/img'
BOTS_DIR = '/bots'
GAMES_DIR = '/games'
OPP_DIR = '/opponents'
PROFILE_FILE = 'profile.p'

# Load a bot's opponent profile. Returns a dict if it exists.
def load_profile(bot_name, opponent_name):
    profile_path = DATA_DIR + BOTS_DIR + '/' + bot_name + OPP_DIR + '/' + opponent_name + '/profile.p'
    if os.path.exists(profile_path):
        return pickle.load(open(profile_path, "rb" ))
    else:
        return None

# Store a bot's opponent profile.
def save_profile(profile, bot_name, opponent_name):
    profile_dir = DATA_DIR + BOTS_DIR + '/' + bot_name + OPP_DIR + '/' + opponent_name + '/profile.p'
    create_dirs(bot_name, opponent_name)
    pickle.dump(profile, open(profile_dir,'wb'))

def save_game_log(bot_name, opponent_name, game_id,log):
    game_path = DATA_DIR + BOTS_DIR + '/' + bot_name + OPP_DIR + '/' + opponent_name + GAMES_DIR + '/'+str(game_id)
    write_to_file(log, game_path)

def read_file(file_name):
    with open(file_name, mode='r') as reader:
        return [line.rstrip() for line in reader]


def write_to_file(text, file_name):
    with open(file_name, mode='w') as writer:
        writer.write(text + "\n")


# Creates directories for bot and opponent.
def create_dirs(bot_name, opponent_name):
    bot_game_dir = DATA_DIR+BOTS_DIR+'/'+bot_name+OPP_DIR+'/'+opponent_name+GAMES_DIR
    img_dir = DATA_DIR+IMG_DIR
    make_dir(bot_game_dir)
    make_dir(img_dir)


def make_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)
