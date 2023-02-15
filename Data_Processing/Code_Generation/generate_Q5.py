# generate_Q5.py
# Author: Aaron Buller
# 2/9/23
# Description: This script will generate and save the Q5 codes for all PRNs currently utilizing the L5 signal

import numpy as np
import json

def main():
    """ Main driver function fo generating the I5 code"""
    # L5 PRNs and Code Advance 
    prn_dict = {"1":1701, "3":5292, "4":2020, "6":7136, "8":5947, "9":4315, "10":148, "11":535, "14":5910, "18":6990, "23":1893, "24":3961, "25":7106, "26":5299, "27":4660, "30":3783, "32":1601}

    code_dict = {}

    SDR_SAMPLE = 22e6

    for sat in prn_dict:
        prn = int(sat)
        delay = prn_dict[sat]

        # Initialize both shift registers 
        xai = [1,1,1,1,1,1,1,1,1,1,1,1,1]
        xbi = get_initialXB(delay)
    
        xa = xai
        xb = xbi

        # Initialize empty list for the I5 code
        i5 = []

        for i in range(10230):
            # Shift both registers to get the new values
            (bval,xb) = shift_XBQ(xb)
            (aval,xa) = shift_XA(xa)

            if xa == [1,1,1,1,1,1,1,1,1,1,1,0,1]:
                xa = [1,1,1,1,1,1,1,1,1,1,1,1,1]

            # Compute the new code value
            new_val = aval^bval

            # Add the code to the list
            i5.append(new_val)

        print(len(i5))
        # Create code dictionary 
        code_dict[str(prn)] = i5

    # Serialize the json object
    json_object = json.dumps(code_dict)
    
    with open("../Codes/Q5_BaseCodes.json",'w') as file:
        file.write(json_object)



def get_initialXB(delay):
    """ Function to shift the XB1 register by the specified delay """

    # Declare the initial register 
    reg = [1,1,1,1,1,1,1,1,1,1,1,1,1]
   
    for i in range(delay):
        # Shift the register by the specified delay
        (val,reg) = shift_XBQ(reg)

    return reg


def shift_XBQ(register):
    """ Shift the XBQ coder by one place and return the new register"""
    # XBI Register Tapped at: 1,3,4,6,7,8,12,13
    tap1 = register[0]^register[2]
    tap2 = register[3]^register[5]
    tap3 = register[6]^register[7]
    tap4 = register[11]^register[12]

    # Compute the new value
    new_val = tap1^tap2^tap3^tap4

    # Create the new register value 
    register.insert(0,new_val)
    register.pop()
    
    return new_val,register


def shift_XA(register):
    """ Shift the XA coder by one place and return the new register """
    # XA Register Tapped at: 9,10,12,13
    tap1 = register[8]^register[9]
    tap2 = register[11]^register[12]

    # Compute the new value
    new_val = tap1^tap2

    # Create the new register
    register.insert(0,new_val)
    register.pop()

    return new_val,register


if __name__=="__main__":
    main()