#!/usr/bin/env python3

"""
Author: Andreas Brecl
Date: 10/25/2022

This script will run the main functionality of the NUC.
"""

# Import libraries
from lib.nuc_serial_comms import NUCSerialComms

def executeFunctions():
    """
    This function will execute the functions for running
    the functionality of the NUC.

    Inputs:  None

    Outputs: None
    """
    # Define initial variables
    serialSpeed = 921600
    serialPort = "/dev/ttyUSB0"
    pathToDisk = "/media/DataStore/"

    # Create objects
    serialComms = NUCSerialComms(serialPort, serialSpeed, pathToDisk)

    # Start fuctions
    serialComms.determineMessageForCube()

def main():
    """
    This excutes the primarity defintions of the main 
    script.
    
    Input:  None

    Output: None
    """
    executeFunctions()

if __name__ == "__main__":
    main()