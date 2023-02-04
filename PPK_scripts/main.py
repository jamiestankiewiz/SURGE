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
    pathToDisk = "D:\Desktop\Past Semesters\Fall 2022\ASEN 5018\PPK_data\\"

    # Get file name
    newFileName = checkForFileNumber(pathToDisk)
    newFileNameAndPath = pathToDisk + newFileName

    # Create serial object
    ser = serial.Serial(
        port="COM4",
        baudrate=38400,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=10
    )

    # Save information to file
    f = open(newFileNameAndPath, "wb")
    while True:

        # Read in data
        data = ser.readline()
    
        # Test prints    
        print(data)

        # Save data
        f.write(data)

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
        newFileName = "PPKdata_" + str(newFileNumber) + ".ubx"    

    else:
        newFileName = "PPKdata_1.txt"

    return newFileName

if __name__ == "__main__":
    main()