import pandas
import pathlib
import warnings

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

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


def boot_plots(x, y_s, labels, line_width = None, x_range = None, y_range = None, colours = None):
    colours_all = ['green', 'blue', 'red', 'black']
    if line_width is None:
        line_width = [0.5, 0.5, 0.5, 0.5]
    if colours is None:
        colours = colours_all[:len(y_s)]
    if x_range is None:
        x_range = [np.min(x), np.max(x)]
    legend_entries = []
    for y, label, colour, lw in zip(y_s, labels, colours, line_width):
        plt.plot(x, y, color=colour, lw=lw)
        legend_entries.append(mpatches.Patch(color=colour, label=label))
    plt.legend(handles=legend_entries)
    axes = plt.gca()
    axes.set_xlim(x_range)
    if y_range is not None:
        axes.set_ylim(y_range)
    plt.xlabel('Frequency(MHz)')
    plt.ylabel('Volts(V)')
    plt.grid()
    return axes