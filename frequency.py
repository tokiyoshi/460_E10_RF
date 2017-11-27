import numpy.polynomial.polynomial as poly

def volt2freq(voltage):
    # Frequency to voltage operations based off of Part A
    V0_const = 708.72
    V1_const = 22.464
    V2_const = -0.0271442

    freqency = V0_const + V1_const * voltage + V2_const * voltage ** 2
    return freqency


def linear_volt2freq(voltage):
    """
    Takes a list of voltages which are expected to be a line, fits the line and then pushes back the linearized
    voltages as frequencies
    Args:
        voltage: A list of voltage values which are expected to be a line
    Return:
        frequency: A list of the linearized frequencies
    """
    x = range(len(voltage))
    coeff = poly.polyfit(x, voltage, 1)
    lin_voltage = coeff[0] + x * coeff[1]
    return volt2freq(lin_voltage), lin_voltage