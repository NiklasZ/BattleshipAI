import os

DATA_DIR = 'data'
BOTS_DIR = '/bots'
GAMES_DIR = '/games'
OPP_DIR = '/opponents'

def read_file(file_name):
    with open(file_name, mode='r') as reader:
        return [line.rstrip() for line in reader]

def write_to_file(text, file_name):
    with open(file_name, mode='wb') as writer:
        writer.write(text+"\n")

#Creates directories for bot and opponent.
def create_dirs_for_bots(bot_name, opponent_name):
    directories = [DATA_DIR, BOTS_DIR, '/'+bot_name, OPP_DIR, '/'+opponent_name, GAMES_DIR]
    current_path = ''
    for d in directory:
        current_path += d
        make_dir(current_path)

    return current_path

def make_dir(path):
    print(path)
    if not os.path.exists(path):
        os.makedirs(path)
