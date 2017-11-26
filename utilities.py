import pandas
import shutil
import pathlib
import warnings

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.ticker import AutoMinorLocator

import numpy as np


def read_folder(scan_number):
    """
    Pathing through the default filestructure to find the channel data
    Args:
        name: number of desirec scan
    Return:
        time: time values of the oscilloscope scan
        channel_1_data: data which was found in the scan 1
        channel_2_data: data which was found in the scan 2
        channel_1_props: dictionary of properties given back by the oscilloscope for the scan #1
        channel_2_props: dictionary of properties given back by the oscilloscope for the scan #2
    """
    if not(0 <= scan_number <= 15):
        raise ValueError('Values outside of the range of 0-15 for scans are not defined')

    top_data_dir = pathlib.Path.cwd().joinpath('data')
    my_data_dir = top_data_dir.joinpath('ALL%04d' % scan_number)

    time, channel_1_data, channel_1_props = read_csv(my_data_dir.joinpath('F%04dCH1.csv' % scan_number))
    time2, channel_2_data, channel_2_props = read_csv(my_data_dir.joinpath('F%04dCH2.csv' % scan_number))

    if not np.array_equal(time, time2):
        if time2 is None:
            warnings.warn('Only Channel 1 Data was found')
        else:
            raise ValueError('Time from channel 1 and channel 2 are not equal... scam %04d' % scan_number)

    return time, channel_1_data, channel_2_data, channel_1_props, channel_2_props


def wipe_folder(path):
    """"
    Just deletes the folder with all subdirectories and then remakes it to wipe it
    Args:
        path: The path to the folder you wish to remove
    Return:
        None
    """
    shutil.rmtree(path, ignore_errors=True)  # Avoiding errors if folder already is gone
    path.mkdir(parents=True)


def read_csv(csv_path):
    """
    Args:
        csv_path: number of desired scan
    Return:
        time: time values of the oscilloscope scan
        data: data which was found in the scan
        properties: dictionary of properties given back by the oscilloscope for the scan
    """
    try:
        data_frame = pandas.read_csv(csv_path, header=None, names=['prop_names', 'prop_vals', 'None', 'time', 'data'],
                                     index_col=False)
        time = np.array(data_frame['time'])
        data = np.array(data_frame['data'])

        properties = {}
        for name, value in zip(data_frame['prop_names'], data_frame['prop_vals']):
            if isinstance(name, str):
                properties[name] = value
        return time, data, properties
    except: # Allowing for possibility of file not existing
        warnings.warn('File: %s \nFatal Crash Occurred, passing back Nones' % csv_path )
        return None, None, None


def boot_plots(x, y_s, labels, y_axis_label, line_width = None, x_range = None, y_range = None, colours = None):
    colours_all = ['green', 'red', 'blue', 'black']
    if line_width is None:
        line_width = [0.3, 0.3, 0.3, 0.3]
    if colours is None:
        colours = colours_all[:len(y_s)]
    if x_range is None:
        x_range = [np.min(x), np.max(x)]
    legend_entries = []
    plt.style.use('bmh')  # You can use different styles in matplotlib Huh
    plt.figure(figsize=(7, 4), dpi=300)
    plt.tight_layout()
    for y, label, colour, lw in zip(y_s, labels, colours, line_width):
        plt.plot(x, y, color=colour, lw=lw)
        legend_entries.append(mpatches.Patch(color=colour, label=label))
    plt.legend(handles=legend_entries)
    axes = plt.gca()
    axes.set_xlim(x_range)
    if y_range is not None:
        axes.set_ylim(y_range)
    plt.xlabel(y_axis_label)
    plt.ylabel('Volts(V)')
    plt.grid()

    axes.xaxis.set_minor_locator(AutoMinorLocator())
    axes.grid(which='minor', alpha=0.2)
    axes.grid(which='major')

    return axes


def point_labeller(axes, type, freq, voltage):
    """
    Just a tool to label the max ans min as I want them on the actual graphs
    """
    if type == 'min':
        min_voltage, min_freq = voltage.min(), freq[np.argmin(voltage)]
        xy_coords = (min_freq, min_voltage)
        text = 'Minimum of %.3f V \nat %.2f MHz' % (min_voltage, min_freq)
        text_coords = (250, 200)
    elif type == 'max':
        max_voltage, max_freq = voltage.max(), freq[np.argmax(voltage)]
        xy_coords = (max_freq, max_voltage)
        text = 'Maximum of %.2f V \nat %.2f MHz' % (max_voltage, max_freq)
        text_coords = (150, -200)
    axes.annotate(text,
                  xy=xy_coords, xycoords='data',
                  xytext=text_coords, textcoords='offset pixels',
                  arrowprops=dict(facecolor='black', shrink=0.05, alpha=.5),
                  horizontalalignment='left', verticalalignment='bottom')


def find_nearest(array, value):
    """
    Find the index of the point which is closest to value for FWHM calculations
    """
    idx = (np.abs(array-value)).argmin()
    return idx