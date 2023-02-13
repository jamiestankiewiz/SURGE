# I5_ResampleCodes.py
# Author: Aaron Buller
# 2/13/23
# Description: This code will resample the I5 codes at the sample rate of the SDR

import scipy.signal
import scipy.interpolate
import numpy as np 
import json
import matplotlib.pyplot as plt


def main():

    # Define the base code rate and SDR sampling rate
    CODE_RATE = 10.230e6
    SDR_RATE = 22e6 
    CODE_PERIOD = 0.001

    # Define the number of points in each of the arrays
    CODE_LENGTH = 10230
    SDR_LENGTH = int(SDR_RATE * CODE_PERIOD)

    # Print the desired code length
    print("Desired Sample Code Length: {}".format(SDR_LENGTH))

    # Define a dictionary to place the final codes
    code_dict = {}
    
    # Create a time vector for each code
    code_time = np.linspace(0,CODE_PERIOD,CODE_LENGTH)
    sdr_time = np.linspace(0,CODE_PERIOD,SDR_LENGTH)

    # Load the code
    with open("../Codes/I5_BaseCodes.json") as file:
        I5_json = json.load(file)


    # Pull out the list of PRNs
    prns = list(I5_json.keys())

    # Loop through each prn and compute the resampled codes
    for prn in prns:
        # Get the original code 
        code = I5_json[prn]

        # Interpolate at the new sampling frequency
        f = scipy.interpolate.interp1d(code_time,code,'nearest')
        new = f(sdr_time)

        # Print the length of the file
        print(len(new))
        
        # Convert the codes from 0s and 1s to 1s and -1s
        new = -1*new
        new[new == 0] = 1 

        # Convert the codes to integer values
        final = [int(i) for i in new]
        
        # Create code dictionary 
        code_dict[prn] = list(final)
    
    # Serialize the json object
    json_object = json.dumps(code_dict)
    
    with open("../Codes/I5_ResampledCodes.json",'w') as file:
        file.write(json_object)
        

        
   

    
if __name__=="__main__":
    main()
