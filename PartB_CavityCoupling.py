from frequency import *  # namespace wont get too cluttered, frequency will be a small module
from utilities import read_folder, wipe_folder, boot_plots

import pathlib

import matplotlib.pyplot as plt

graph_dir = pathlib.Path.cwd().joinpath('graphs')
wipe_folder(graph_dir)

# For scopes with CH1 as freq ramp
for scope, title in zip([0, 1, 2, 3, 4], ['Attempt1', 'Critical Coupling Condition (10Hz)', 'Minimal Coupling', 'Midway Coupling Condition (10Hz)']):
    time, channel_1_data, channel_2_data, channel_1_props, channel_2_props = read_folder(scope)
    if channel_2_data is None:
        boot_plots(time, [channel_1_data], ['CH1'], 'Time(s)')
    else:
        ch1_freq = linear_volt2freq(channel_1_data)
        boot_plots(time, [channel_1_data, channel_2_data], ['CH1', 'CH2'], 'Time(s)')
        plt.savefig(str(graph_dir.joinpath('scope_%s_raw.png' % scope)))
        plt.close()
        boot_plots(ch1_freq, [channel_2_data], ['Response'], 'Frequency(MHz)')
        plt.title(title)
    plt.savefig(str(graph_dir.joinpath('scope_%s.png' % scope)))
    plt.close()

# Scopes where we wish to just see both channels against time
for scope, title in zip([5, 6], ['Transmission', 'Maximal Transmission']):
    time, channel_1_data, channel_2_data, channel_1_props, channel_2_props = read_folder(scope)
    boot_plots(time, [channel_1_data, channel_2_data], ['CH1', 'CH2'], 'Time(s)')
    plt.savefig(str(graph_dir.joinpath('scope_%s.png' % scope)))
    plt.title(title)
    plt.close()

# Scopes with CH2 as freq ramp
for scope, title in zip([8, 10, 11, 14], ['Maximal Transmission (2Hz)', 'Maximal Transmission (10Hz)', 'Maximal Coupling (10Hz)', 'Anti-Symmetric Cavity Reflection']):
    time, channel_1_data, channel_2_data, channel_1_props, channel_2_props = read_folder(scope)
    ch2_freq = linear_volt2freq(channel_2_data)
    boot_plots(ch2_freq, [channel_1_data], ['Response'], 'Frequency(MHz)')
    plt.savefig(str(graph_dir.joinpath('scope_%s.png' % scope)))
    plt.title(title)
    plt.close()

# Scopes to just print everything in case
for scope, title in zip([12, 15], ['Anti-Symmetric Cavity Reflection', 'Symmetric Cavity Reflection']):
    time, channel_1_data, channel_2_data, channel_1_props, channel_2_props = read_folder(scope)
    if channel_2_data is None:
        boot_plots(time, [channel_1_data], ['CH1'], 'Time(s)')
    else:
        boot_plots(time, [channel_1_data, channel_2_data], ['CH1', 'CH2'], 'Time(s)')
    plt.savefig(str(graph_dir.joinpath('scope_%s_raw.png' % scope)))
    plt.title(title)
    plt.close()