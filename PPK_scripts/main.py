#!/usr/bin/env python3

"""
Author: Andreas Brecl, Aaron Buller, Sean Newman
Date: 02/01/2023

This script will run the PPK to save software to the NUC.
"""

# Import libraries
import time
import os
import serial
import serial.tools.list_ports

def main():
    """
    This will run the main functionality of the PPK to NUC
    file saving.

    Input:  None

    Output: None
    """
    # Define base variables
    pathToDisk = "/media/PPK_data/"

    # Get file name
    newFileName = checkForFileNumber(pathToDisk)
    newFileNameAndPath = pathToDisk + newFileName

    # Get the path of the USB port
    usb_path = getCommPort()

    # Create serial object
    ser = serial.Serial(
        port=usb_path,
        baudrate=38400,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=10
    )

    # Save information to file
    f = open(newFileNameAndPath, "wb")

    try:
        while True:

            # Read in data
            data = ser.readline()

            # Save data
            f.write(data)

    except:
        # Close the file and serial
        f.close()
        ser.close()

def checkForFileNumber(pathToDisk):
    """
    This function will check for the current file number that
    has been written the output the number that the new file
    needs.

    Input:  pathToDisk <str> - Path to save location

    Output: newFileName <str> - New file name to write to
    """
    # Define checker vars
    fileNumber = 0

    # Pull list of files in directory
    directoryList = os.listdir(pathToDisk)

    # Iterate through files
    if directoryList != None:
        for file in directoryList:
            splitFile = file.split("_")
            splitFileSecond = splitFile[1].split(".")
            fileNumberCurrent = int(splitFileSecond[0])

            # See if number is larger
            if fileNumberCurrent > fileNumber:
                fileNumber = fileNumberCurrent

        # Create new file name
        newFileNumber = fileNumber + 1
        newFileName = "PPKdata_" + str(newFileNumber) + "_" + time.strftime("%Y-%m-%d-%H:%M:%S") + ".ubx"    

    else:
        newFileName = "PPKdata_1" + "_" + time.strftime("%Y-%m-%d-%H:%M:%S") + ".ubx"

    return newFileName

def getCommPort():
    """ Return the file path of the comm port that the """

    # Get all the active com ports 
    ports = serial.tools.list_ports.comports()

    # Loop through all ports to find the gps reciever
    for port in ports:
        description = port.description
        if description == "u-blox GNSS receiver":
            usb_path = port.device
            return usb_path
    

if __name__ == "__main__":
    main()