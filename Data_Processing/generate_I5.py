# generate_I5.py
# Author: Aaron Buller
# 2/9/23
# Description: This script will generate and save the I5 codes for all PRNs currently utilizing the L5 signal

import numpy as np
import json

def main():
    """ Main driver function fo generating the I5 code"""
    # L5 PRNs and Code Advance 
    prn_dict = {"1":266, "3":804, "4":1138, "6":1559, "8":2084, "9":2170, "10":2303, "11":2527, "14":3471, "18":4924, "23":5898, "24":5918, "25":5955, "26":6243, "27":6345, "30":6875, "32":7187}

    code_dict = {}

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
            (bval,xb) = shift_XBI(xb)
            (aval,xa) = shift_XA(xa)

            # Compute the new code value
            new_val = aval^bval

            # Add the code to the list
            i5.append(new_val)

        print(len(i5))
        # Create code dictionary 
        code_dict[str(prn)] = i5

    # Serialize the json object
    json_object = json.dumps(code_dict)
    
    with open("I5_Codes.json",'w') as file:
        file.write(json_object)



def get_initialXB(delay):
    """ Function to shift the XB1 register by the specified delay """

    # Declare the initial register 
    reg = [1,1,1,1,1,1,1,1,1,1,1,1,1]
   
    for i in range(delay):
        # Shift the register by the specified delay
        (val,reg) = shift_XBI(reg)

    return reg


def shift_XBI(register):
    """ Shift the XBI coder by one place and return the new register"""
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
    