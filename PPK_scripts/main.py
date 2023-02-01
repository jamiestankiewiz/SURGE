#!/usr/bin/env python3

"""
Author: Andreas Brecl
Date: 02/01/2023

This script will run the PPK to save software to the NUC.
"""

# Import libraries
import time
import os
import serial

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

    # Create serial object
    ser = serial.Serial(
        port='/dev/serial0',
        baudrate=38400,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=10
    )

    # Save information to file
    f = open(newFileNameAndPath, "a")
    while ser.read():

        # Read in data
        data = str(ser.readline())

        # Save data
        f.writelines(data)

    # Close the file
    f.close()

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
            splitFileSecond = splitFile.split(".")
            fileNumberCurrent = int(splitFileSecond[0])

            # See if number is larger
            if fileNumberCurrent > fileNumber:
                fileNumber = fileNumberCurrent

        # Create new file name
        newFileNumber = fileNumber + 1
        newFileName = "PPKdata_" + str(newFileNumber) + ".txt"    

    else:
        newFileName = "PPKdata_1.txt"

    return newFileName

if __name__ == "__main__":
    main()