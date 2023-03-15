# test_correlate.py 
# Author: Aaron Buller
# 2/22/23
# Description: Test the correlation properties of the L5 codes

import json
import numpy as np 
import scipy.signal as sig
import matplotlib.pyplot as plt
import scipy.io
import csv 

# Define the base code rate and SDR sampling rate
CODE_RATE = 10.230e6
SDR_RATE = 22e6 
CODE_PERIOD = 0.001

# Define the number of points in each of the arrays
CODE_LENGTH = 10230
SDR_LENGTH = int(SDR_RATE * CODE_PERIOD)

# Define max and min doppler ranges
MAX_DOPPLER = 1000

with open("Codes/Q5_BaseCodes.json",'r') as q5file:
    q5json = json.load(q5file)

with open("Codes/I5_BaseCodes.json",'r') as i5file:
    i5json = json.load(i5file)

with open("Output.csv",'r') as SDR_File:
    sdr = csv.reader(SDR_File,delimiter=',')
    for row in sdr:
        a = row

sdr_data = np.array([np.complex128(dat) for dat in a])

sig1 = i5json["9"]
# Use next 2 lines for base codes
sig1 = np.array(sig1) * -1
sig1[sig1 == 0] = 1

sig2 = q5json["32"]
sig2 = np.array(sig2) * -1
sig2[sig2 == 0] = 1 

# Generate a range of Doppler shifts to search over
doppler_shifts = np.linspace(-MAX_DOPPLER, MAX_DOPPLER, num=int(CODE_LENGTH/101))
#doppler_shifts = [0]

#correlation_results = np.zeros((len(doppler_shifts), CODE_LENGTH), dtype=complex)
correlation_results = np.zeros((len(doppler_shifts), 2*CODE_LENGTH), dtype=complex)


shifted = np.roll(sig1,5000)


# Loop through the possible Doppler 
for i, doppler in enumerate(doppler_shifts):

    # Apply the doppler shift to the 
    #shifted_signal = np.array(shifted) * np.exp(2j*doppler*np.pi)
    shifted_signal = sdr_data[:10231] * np.exp(2j*doppler*np.pi)

    # Correlate the y axis
    ycor = sig.correlate(sig1,shifted_signal,mode='full',method='auto')

   

    # Separate the negative side of the fft and flip
    #cor = np.flip(ycor[0:10230])

    

    # Get the absolute value
    cor_abs = ycor #np.absolute(cor)


    correlation_results[i,:] = cor_abs

final_data = {}
#print(correlation_results[12,:])
final_data["correlation"] = correlation_results


scipy.io.savemat('/Users/aaronb/Documents/MATLAB/Grad_Projects/cor_data.mat',final_data)

