
import src.utils.fileIO as io
import src.ai.bot_learning as bot_learn
import src.ai.heuristics as heur

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def plot_performance_vs_opponent(bot_names, opponent_name, running_avg_window, game_count):
    bot_data = {'win rate': {},
                'accuracy': {},
                'evasion': {}}
    colours = ('b', 'g', 'r', 'c', 'm', 'y', 'k')

    for name in bot_names:
        profile = io.load_profile(name, opponent_name)
        games = profile['games']
        first_games = sorted(games)[:game_count]
        bot_data['win rate'][name] = calculate_win_rates([games[i]['victory'] for i in first_games])
        bot_data['accuracy'][name] = [games[i]['accuracy'] for i in first_games]
        bot_data['evasion'][name] = [games[i]['evasion'] for i in first_games]

    handles = []
    f, axarr = plt.subplots(len(bot_data), sharex=True)
    for idx, measure in enumerate(bot_data):
        for bot, c in zip(bot_data[measure], colours):
            data_frame = pd.DataFrame(bot_data[measure][bot])
            smoothed = data_frame.rolling(window=running_avg_window).mean().as_matrix()
            if measure == 'win rate':
                overall_mean = bot_data[measure][bot][-1]
            else:
                overall_mean = np.average(bot_data[measure][bot])
            handles.append(axarr[idx].plot(smoothed, c, label=bot + ' - AVG ' + '{:.2f}'.format(overall_mean)))

        axarr[idx].set_title(opponent_name + ' - ' + measure)
        axarr[idx].set_ylabel('percentage')
        # axarr[idx].set_xlabel('First 100 games')
        #axarr[idx].set_ylim((0, 1))
        axarr[idx].legend()

    plt.savefig(io.DATA_DIR + io.IMG_DIR + '/perf_vs_' + opponent_name + '.svg')
    plt.show()


def calculate_win_rates(wins):
    converted = np.multiply(wins, 1)
    win_avg = []
    win_sum = 0
    for idx, w in enumerate(converted):
        win_sum += w
        win_avg.append(win_sum / (idx + 1))

    return win_avg


def plot_heuristic_vs_opponent(bot_location, bot_name, opponent_name, game_count, heuristic_name, heuristic_values, repetitions,file_name_suffix='',):


    sampled_performances = [[]]*repetitions
    for i in range(repetitions):
        sampled_performances[i] = heuristic_vs_opponent(bot_location,bot_name, opponent_name, game_count, heuristic_name, heuristic_values)
        plt.plot(heuristic_values,sampled_performances[i])
    plt.xlabel('Values of '+heuristic_name)
    plt.ylabel('Loss (Misses) obtained')
    plt.title(bot_name+' heuristic '+heuristic_name+' performance vs. '+opponent_name)
    plt.savefig(io.DATA_DIR + io.IMG_DIR + '/'+bot_name+'_'+heuristic_name+'_perf_vs_' + opponent_name + file_name_suffix+'.svg')
    plt.show()


def heuristic_vs_opponent(bot_location, bot_name, opponent_name, game_count, heuristic_name, heuristic_values):

    performances = []
    for h_val in heuristic_values:
        o = bot_learn.Optimiser(bot_name, opponent_name, bot_location)
        game_dict = o.opponent_profile['games']
        games = [g for g in sorted(game_dict, reverse=True)[:game_count]]
        o.prepare_heuristics([heuristic_name])
        o.prepare_offensive_games(games)
        o.set_optimisation_type('minimise')
        result = o.play_games([h_val])
        print('Final avg:', '{:.3f}'.format(result))
        performances.append(result)

    return performances

# plot_performance_vs_opponent(['bouillabaisse', 'gazpacho','pho'], 'housebot-master', 12, 100)

bot_location = 'src.ai.bots' + '.pho'
start = heur.SEARCH_RANGES['ship_adjacency'][0]
stop = heur.SEARCH_RANGES['ship_adjacency'][1]
heuristic_values = np.linspace(start,stop,num=20)
plot_heuristic_vs_opponent(bot_location, 'pho', 'housebot-competition', 10, 'ship_adjacency', heuristic_values,5,'multi_test-20val-10g')



