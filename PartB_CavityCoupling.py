from frequency import *  # namespace wont get too cluttered, frequency will be a small module
from utilities import read_folder

time, channel_1_data, channel_2_data, channel_1_props, channel_2_props = read_folder(0)
ch1_freq = linear_volt2freq(channel_1_data)