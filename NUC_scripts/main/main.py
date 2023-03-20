#!/usr/bin/env python3

"""
Author: Andreas Brecl
Date: 10/25/2022

This script will run the main functionality of the NUC.
"""

# Import time
from time import time
import subprocess, os
import signal

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
        #rpistr = "python3 /home/gpsadmin/Desktop/Code/test_scripts/mavlink_send_1_and_0.py"
        rpistr = "python3 /home/gpsadmin/Desktop/Code/test_scripts/mavlink_send_1_and_0.py"
        Mode = serialComms.getFlightMode()
        running = 0

        print(Mode)
        
        if Mode == 'Guided' and running == 0:
            running = 1

            p=subprocess.Popen(rpistr, shell=True, preexec_fn=os.setsid)
        elif Mode != 'Guided' and running == 1:
            os.killpg(p.pid, signal.SIGTERM)
            running = 0




if __name__ == "__main__":
    main()