import matplotlib.pyplot as plt
import src.utils.fileIO as io

import numpy as np
import os
import pandas as pd

os.chdir('..')  # very lazy fix.


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
        axarr[idx].set_ylim((0, 1))
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


plot_performance_vs_opponent(['bouillabaisse', 'gazpacho'], 'housebot-master', 12, 400)
