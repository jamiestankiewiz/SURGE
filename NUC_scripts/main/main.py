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
    running = 0

    # Run main loop
    while True:

        # Start fuctions
        serialComms.determineMessageForCube()
        Mode = serialComms.getFlightMode()
        if Mode == -1:
          continue
        Mode = Mode.lower()
        Mode_list = ['guided','loiter','stabilize','auto','land','alt hold','circle']
        #print(Mode)
        rpistr = "sudo -u gpsadmin -H /home/gpsadmin/uhd_ext-ncl2/rx_multi_to_file --settings /home/gpsadmin/uhd_ext-ncl2/b210_split_settings-balloon.xml --time -1"
        if Mode in Mode_list:
          #print(Mode)
          if Mode == 'auto' and running == 0:
              running = 1
              #print("Me Here")
              p=subprocess.Popen(rpistr, shell=True, preexec_fn=os.setsid)
          elif Mode != 'auto' and running == 1:
              os.killpg(p.pid, signal.SIGTERM)
              running = 0
if __name__ == "__main__":
    main()
