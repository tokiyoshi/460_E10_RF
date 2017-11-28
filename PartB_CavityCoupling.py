from frequency import *  # namespace wont get too cluttered, frequency will be a small module
from utilities import read_folder, wipe_folder, boot_plots, point_labeller, find_nearest

import pathlib

import numpy as np
import matplotlib.pyplot as plt

from scipy.signal import savgol_filter


def gamma_sq(Q_l, res_freq, freq):
    delta_freq = abs(freq - res_freq)
    denominator = 1 + 4 * (Q_l ** 2) * 2 * 3.1415 *(delta_freq/res_freq) ** 2
    return 1 - (1/denominator)


def V2P(voltage):
    power = 0.0055 * (voltage ** 1.5) + 0.0051 * (voltage ** 2.7) + 0.0026 * (voltage ** 0.5) + 0.011 * (voltage ** 1.6)
    error = power * 22.218 - 22.1578 * voltage
    error[voltage > 1.0] = power[voltage > 1.0] * 0.058
    return power


graph_dir = pathlib.Path.cwd().joinpath('graphs')
wipe_folder(graph_dir)


# For scopes with CH1 as freq ramp
for scope, title in zip([0, 1, 2, 3, 4], ['Attempt1', 'Critical Coupling Condition (10Hz)', 'Minimal Coupling', 'Midway Coupling Condition (10Hz)', 'Maximal Coupling Condition (2Hz)']):
    time, channel_1_data, channel_2_data, channel_1_props, channel_2_props = read_folder(scope)
    if channel_2_data is None:
        boot_plots(time, [channel_1_data], ['CH1'], 'Time(s)')
    else:
        ch1_freq, ch1_linvoltage = linear_volt2freq(channel_1_data)
        if scope == 2:
            minimal_reflect = channel_2_data
        boot_plots(time, [channel_1_data, channel_2_data, ch1_linvoltage], ['CH1', 'CH2', 'CH1 fit'], 'Time(s)')
        plt.title('%s : Raw Data' % title)
        plt.savefig(str(graph_dir.joinpath('scope_%s_raw.png' % scope)))
        plt.close()
        axes = boot_plots(ch1_freq, [channel_2_data], ['Cavity Response'], 'Frequency(MHz)', y_range=[0,1.1])
        if scope in (0, 1, 4):
            point_labeller(axes, 'min', ch1_freq, channel_2_data)
        plt.title(title)
    plt.savefig(str(graph_dir.joinpath('scope_%s.png' % scope)))
    plt.close()

# Scopes where we wish to just see both channels against time
for scope, title in zip([5, 6], ['Weak (20%) Transmission', 'Maximal Transmission']):
    time, channel_1_data, channel_2_data, channel_1_props, channel_2_props = read_folder(scope)
    boot_plots(time, [channel_1_data, channel_2_data], ['CH1', 'CH2'], 'Time(s)')
    plt.title(title)
    plt.savefig(str(graph_dir.joinpath('scope_%s.png' % scope)))
    plt.close()

# Scopes with CH2 as freq ramp
for scope, title in zip([10, 8, 11, 14], ['Maximal Transmission (10Hz)', 'Maximal Transmission (2Hz)', 'Maximal Coupling (10Hz)', 'Anti-Symmetric Cavity Reflection']):
    time, channel_1_data, channel_2_data, channel_1_props, channel_2_props = read_folder(scope)
    ch2_freq, ch2_linvoltage = linear_volt2freq(channel_2_data)
    boot_plots(time, [channel_1_data, channel_2_data, ch2_linvoltage], ['CH1', 'CH2', 'CH2 fit'], 'Time(s)')
    plt.title('%s : Raw Data' % title)
    plt.savefig(str(graph_dir.joinpath('scope_%s_raw.png' % scope)))
    plt.close()
    axes = boot_plots(ch2_freq, [channel_1_data], ['Cavity Response'], 'Frequency(MHz)')
    if scope in (8, 10):
        point_labeller(axes, 'max', ch2_freq, channel_1_data)

        # We also wish to find FWHM here... jenky code but its one time use
        max_voltage = channel_1_data.max()
        max_index = np.argmax(channel_1_data)

        FWHM_index_low, FWHM_index_high = find_nearest(channel_1_data[:max_index], max_voltage/2), max_index + find_nearest(channel_1_data[max_index:], max_voltage/2)
        FEHM_low, FWHM_high = ch2_freq[FWHM_index_low], ch2_freq[FWHM_index_high]

        FWHM = abs(FWHM_high - FEHM_low)
        title = '%s : FWHM = %.2f MHz' % (title, FWHM)
        plt.title(title)
        plt.savefig(str(graph_dir.joinpath('scope_%s.png' % scope)))
        plt.close()

        Q_l = ch2_freq[max_index]/FWHM

        print('For graph %s we have %s as the quality factor' % (title, Q_l))

        gamma = gamma_sq(Q_l, ch2_freq[max_index], ch2_freq)

        axes = boot_plots(ch2_freq, [gamma], ['Power Reflection Coefficent '], 'Frequency(MHz)', y_axis='$|\Gamma|^2$')
        plt.title('Power Reflection Coefficent($|\Gamma|^2$) vs Frequency')
        plt.savefig(str(graph_dir.joinpath('gamma.png')))
        plt.close()

        if scope == 10:
            reflect_freq = ch2_freq
        if scope == 8:
            reflect_res = ch2_freq[max_index]

    if scope == 11:
        _, min_freq = point_labeller(axes, 'min', ch2_freq, channel_1_data)
        plt.title(title)

        plt.savefig(str(graph_dir.joinpath('scope_%s.png' % scope)))
        plt.close()

        raw_reflect = V2P(channel_1_data)
        min_reflect = V2P(minimal_reflect)

        gamma = gamma_sq(Q_l, min_freq, reflect_freq)

        reflect_filter = savgol_filter(raw_reflect, 7, 3)
        calc_filter = savgol_filter(min_reflect * gamma, 7, 3)

        subtracted_signal = savgol_filter(np.abs(raw_reflect - (min_reflect * gamma)), 9, 3)

        boot_plots(reflect_freq,
                   #[gauss(raw_reflect, 3), gauss(min_reflect * gamma, 3)],
                   [reflect_filter, calc_filter],
                   ['Raw Reflection', 'Calculated Reflection'], 'Frequency(MHz)', y_axis="Power (W)", line_width=[0.5, 0.5])
        plt.title('Calculated and Actual Reflected Power')
        plt.savefig(str(graph_dir.joinpath('reflect_savgol.png')))
        plt.close()

        boot_plots(reflect_freq,
                   [raw_reflect, min_reflect * gamma],
                   # [gauss(raw_reflect, 3), gauss(min_reflect * gamma, 3)],
                   #[savgol_filter(raw_reflect, 7, 3), savgol_filter(min_reflect * gamma, 7, 3)],
                   ['Raw Reflection', 'Calculated Reflection'], 'Frequency(MHz)', y_axis="Power (W)", line_width=[0.5, 0.5])
        plt.title('Calculated and Actual Reflected Power')
        plt.savefig(str(graph_dir.joinpath('reflect_raw.png')))
        plt.close()

        boot_plots(reflect_freq, [subtracted_signal], ['Subtracted Reflections'], 'Frequency(MHz)', y_axis="Power (W)",)
        plt.title('Difference Between Calculated and Actual Signal')
        plt.savefig(str(graph_dir.joinpath('reflect_sub.png')))
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
