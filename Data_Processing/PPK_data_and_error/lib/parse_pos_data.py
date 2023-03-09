#!/usr/bin/env python3

"""
Author: Andreas Brecl
Date: 03/08/2023

This script will parse PPK pos file.
"""

class ParsePOSData:
    def __init__(self, fileName):
        """
        This initialized the variable names and the object for parsing POS file.

        Input:  fileName <str> - Name of POS file and path

        Output: None
        """

        # Define variables
        self.fileName = fileName

    def getPOSData(self):
        """
        This gets the POS file data. The ref position is pulled, the GPST, lat, long,
        and height.

        Input:  None

        Output: GPST <list><str> - GPST time of collection
                latitude <list><float> - Latitude of position
                longitude <list><float> - Longitude of positon
                height <list><float> - Height of position
                refPos <list> - Reference position
                Q <list><int> - Signal quality
        """
        # Open the file
        with open(self.fileName, mode="r") as file:

            # Read the file
            lineData = file.readlines()

        # Check for reference positions
        for lineRef in lineData:

            # Split line
            lineSplit = lineRef.split(" ")

            # Check for line
            if len(lineSplit) > 1:
                if lineSplit[1] == "ref":
                    
                    # Save ref data
                    refPosLat = float(lineSplit[6])
                    refPosLon = float(lineSplit[7])
                    refPosHeight = float(lineSplit[9].split('\n')[0])
                    refPos = [refPosLat, refPosLon, refPosHeight]

                    # Break loop
                    break

        # Preallocate vars
        startDataRead = False
        GPST = []
        latitude = []
        longitude = []
        height = []
        Q = []

        # Pull other positioning data
        for linePos in lineData:

            # Split line
            lineSplit = linePos.split(" ")

            # Read in data
            if startDataRead == True:
                
                # Save data
                GPST.append([lineSplit[0], lineSplit[1]])
                latitude.append(float(lineSplit[4]))
                longitude.append(float(lineSplit[5]))
                height.append(float(lineSplit[7]))
                Q.append(int(lineSplit[10]))

            # Check if data is being read
            if len(lineSplit) > 1 and startDataRead == False:
                if lineSplit[2] == "GPST":
                    startDataRead = True

        return GPST, latitude, longitude, height, Q, refPos