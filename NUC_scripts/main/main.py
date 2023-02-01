#!/usr/bin/env python3

"""
Author: Andreas Brecl
Date: 10/25/2022

This script will run the main functionality of the NUC.
"""

# Import time
from time import time

# Import libraries
from lib.nuc_serial_comms import NUCSerialComms

def main():
    """
    This function will execute the functions for running
    the functionality of the NUC.

    Inputs:  None

    Outputs: None
    """
    # Define initial variables
    serialSpeed = 921600
    serialPort = "/dev/ttyUSB0"
    pathToDisk = "/media/DataStore/usrp3"

    # Create objects
    serialComms = NUCSerialComms(serialPort, serialSpeed, pathToDisk)

    # Run main loop
    while True:

        # Start fuctions
        serialComms.determineMessageForCube()

if __name__ == "__main__":
    main()