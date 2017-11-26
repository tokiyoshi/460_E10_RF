from frequency import *  # namespace wont get too cluttered, frequency will be a small module
from utilities import read_folder, wipe_folder, boot_plots, point_labeller, find_nearest

import pathlib

import numpy as np
import matplotlib.pyplot as plt

graph_dir = pathlib.Path.cwd().joinpath('graphs')
wipe_folder(graph_dir)

# For scopes with CH1 as freq ramp
for scope, title in zip([0, 1, 2, 3, 4], ['Attempt1', 'Critical Coupling Condition (10Hz)', 'Minimal Coupling', 'Midway Coupling Condition (10Hz)', 'Maximal Coupling Condition (2Hz)']):
    time, channel_1_data, channel_2_data, channel_1_props, channel_2_props = read_folder(scope)
    if channel_2_data is None:
        boot_plots(time, [channel_1_data], ['CH1'], 'Time(s)')
    else:
        ch1_freq = linear_volt2freq(channel_1_data)
        boot_plots(time, [channel_1_data, channel_2_data], ['CH1', 'CH2'], 'Time(s)')
        plt.savefig(str(graph_dir.joinpath('scope_%s_raw.png' % scope)))
        plt.close()
        axes = boot_plots(ch1_freq, [channel_2_data], ['Cavity Response'], 'Frequency(MHz)', y_range=[0,1.1])
        if scope in (0, 1, 4):
            point_labeller(axes, 'min', ch1_freq, channel_2_data)
        plt.title(title)
    plt.savefig(str(graph_dir.joinpath('scope_%s.png' % scope)))
    plt.close()

# Scopes where we wish to just see both channels against time
for scope, title in zip([5, 6], ['Transmission', 'Maximal Transmission']):
    time, channel_1_data, channel_2_data, channel_1_props, channel_2_props = read_folder(scope)
    boot_plots(time, [channel_1_data, channel_2_data], ['CH1', 'CH2'], 'Time(s)')
    plt.title(title)
    plt.savefig(str(graph_dir.joinpath('scope_%s.png' % scope)))
    plt.close()

# Scopes with CH2 as freq ramp
for scope, title in zip([8, 10, 11, 14], ['Maximal Transmission (2Hz)', 'Maximal Transmission (10Hz)', 'Maximal Coupling (10Hz)', 'Anti-Symmetric Cavity Reflection']):
    time, channel_1_data, channel_2_data, channel_1_props, channel_2_props = read_folder(scope)
    ch2_freq = linear_volt2freq(channel_2_data)
    axes = boot_plots(ch2_freq, [channel_1_data], ['Cavity Response'], 'Frequency(MHz)')
    if scope in (8, 10):
        point_labeller(axes, 'max', ch2_freq, channel_1_data)
        # We also wish to find FWHM here... jenky code but its one time use
        max_voltage = channel_1_data.max()
        max_index = np.argmax(channel_1_data)

        FWHM_index_low, FWHM_index_high = find_nearest(channel_1_data[:max_index], max_voltage/2), max_index + find_nearest(channel_1_data[max_index:], max_voltage/2)
        FEHM_low, FWHM_high = ch2_freq[FWHM_index_low], ch2_freq[FWHM_index_high]

        FWHM = abs(FWHM_high - FEHM_low)
        title = '%s : with FWHM of %.2f' % (title, FWHM)
    if scope == 11:
        point_labeller(axes, 'min', ch2_freq, channel_1_data)
    plt.title(title)
    plt.savefig(str(graph_dir.joinpath('scope_%s.png' % scope)))
    plt.close()

# Scopes to just print everything in case
for scope, title in zip([12, 15], ['Anti-Symmetric Cavity Reflection', 'Symmetric Cavity Reflection']):
    time, channel_1_data, channel_2_data, channel_1_props, channel_2_props = read_folder(scope)
    if channel_2_data is None:
        boot_plots(time, [channel_1_data], ['CH1'], 'Time(s)')
    else:
        boot_plots(time, [channel_1_data, channel_2_data], ['CH1', 'CH2'], 'Time(s)')
    plt.title(title)

    plt.savefig(str(graph_dir.joinpath('scope_%s_raw.png' % scope)))
    plt.close()