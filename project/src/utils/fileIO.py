import os
import pickle

DATA_DIR = '../data'
IMG_DIR = '/img'
BOTS_DIR = '/bots'
GAMES_DIR = '/games'
OPP_DIR = '/opponents'
PROFILE_FILE = 'profile.p'
GAMES_LOG_FILE = 'log.p'


# Load a bot's opponent profile. Returns a dict if it exists.
def load_profile(bot_name, opponent_name):
    profile_path = DATA_DIR + BOTS_DIR + '/' + bot_name + OPP_DIR + '/' + opponent_name + '/profile.p'
    load_pickle_if_exists(profile_path)


# Store a bot's opponent profile.
def save_profile(profile, bot_name, opponent_name):
    profile_dir = DATA_DIR + BOTS_DIR + '/' + bot_name + OPP_DIR + '/' + opponent_name + '/profile.p'
    create_dirs(bot_name, opponent_name)
    pickle.dump(profile, open(profile_dir, 'wb'))


def save_game_log(bot_name, opponent_name, game_id, log, pickled_log):
    game_log_path = DATA_DIR + BOTS_DIR + '/' + bot_name + OPP_DIR + '/' + opponent_name + GAMES_DIR + '/' + str(
        game_id)
    game_pickled_log_path = DATA_DIR + BOTS_DIR + '/' + bot_name + OPP_DIR + '/' + opponent_name + GAMES_DIR + '/' + GAMES_LOG_FILE
    write_to_file(log, game_log_path)
    pickle.dump(pickled_log, open(game_pickled_log_path, 'wb'))


def load_pickled_game_log(bot_name, opponent_name):
    game_log_path = DATA_DIR + BOTS_DIR + '/' + bot_name + OPP_DIR + '/' + opponent_name + GAMES_DIR + '/' + GAMES_LOG_FILE
    load_pickle_if_exists(game_log_path)


def load_pickle_if_exists(path):
    if os.path.exists(path):
        return pickle.load(open(path, "rb"))
    else:
        return None


def read_file(file_name):
    with open(file_name, mode='r') as reader:
        return [line.rstrip() for line in reader]


def write_to_file(text, file_name):
    with open(file_name, mode='w') as writer:
        writer.write(text + "\n")


# Creates directories for bot and opponent.
def create_dirs(bot_name, opponent_name):
    bot_game_dir = DATA_DIR + BOTS_DIR + '/' + bot_name + OPP_DIR + '/' + opponent_name + GAMES_DIR
    img_dir = DATA_DIR + IMG_DIR
    make_dir(bot_game_dir)
    make_dir(img_dir)


def make_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)
