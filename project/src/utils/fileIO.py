import os
import pickle

DATA_DIR = '../data'
BOTS_DIR = '/bots'
GAMES_DIR = '/games'
OPP_DIR = '/opponents'
PROFILE_FILE = 'profile.p'

# Load a bot's opponent profile. Returns a dict if it exists.
def load_profile(bot_name, opponent_name):
    profile_dir = DATA_DIR + BOTS_DIR + '/' + bot_name + OPP_DIR + '/' + opponent_name + '/profile.p'
    if os.path.exists(profile_dir):
        return pickle.load(open( profile_dir, "rb" ))
    else:
        return None

# Store a bot's opponent profile.
def store_profile(profile, bot_name, opponent_name):
    profile_dir = DATA_DIR + BOTS_DIR + '/' + bot_name + OPP_DIR + '/' + opponent_name + '/profile.p'
    create_dirs_for_bots(bot_name, opponent_name)
    pickle.dump(profile, open(profile_dir,'wb'))


def read_file(file_name):
    with open(file_name, mode='r') as reader:
        return [line.rstrip() for line in reader]


def write_to_file(text, file_name):
    with open(file_name, mode='w') as writer:
        writer.write(text + "\n")


# Creates directories for bot and opponent.
def create_dirs_for_bots(bot_name, opponent_name):
    directories = [DATA_DIR, BOTS_DIR, '/' + bot_name, OPP_DIR, '/' + opponent_name, GAMES_DIR]
    current_path = ''
    for d in directories:
        current_path += d
        make_dir(current_path)

    return current_path


def make_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)
