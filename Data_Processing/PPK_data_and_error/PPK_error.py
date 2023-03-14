#!/usr/bin/env python3

"""
Author: Andreas Brecl
Date: 03/08/2023

This script will calculate the PPK error bounds.
"""

from lib.parse_pos_data import ParsePOSData
from statistics import mean
from pymap3d import geodetic2enu
from math import sqrt, pow
import numpy as np
import matplotlib.pyplot as plt

def main():
    """
    This will run the main functionality of the PPK to NUC
    file saving.

    Input:  None

    Output: None
    """

    # Enter file name
    fileName = 'PPKdata_8.pos'

    # Find path to file
    currentFile = str(__file__).split('/')
    currentFile = currentFile[:-1]
    currentFile = '\\'.join(currentFile)
    fileName = currentFile + '\data_files\\' + fileName

    # Define file object
    errorFile = ParsePOSData(fileName)

    # Pull file data
    _, latitude, longitude, height, Q, _ = errorFile.getPOSData()

    # Calculate STD sigma
    distaneListENU = calculateSigmaAndMean(latitude, longitude, height, Q)

    # Plot values
    plotErrorValues(distaneListENU)

def plotErrorValues(distaneListENU):
    """
    This function will plot the resulting values form the error calculations.

    Inupt:  distaneListENU <list> - ENU Positions

    Output: None
    """
    # Convert ENU values to numpy array
    distanceListENUEast = np.array([distanceENU[0] for distanceENU in distaneListENU])*100
    distanceListENUNorth = np.array([distanceENU[1] for distanceENU in distaneListENU])*100
    distanceListENUHei = np.array([distanceENU[2] for distanceENU in distaneListENU])*100

    # Create scatter plot
    plt.figure()
    plt.scatter(distanceListENUEast, distanceListENUNorth)
    plt.xlabel('East Error [cm]')
    plt.ylabel('North Error [cm]')
    plt.title('ENU Error')

    # Show plot
    plt.show()

def calculateSigmaAndMean(latitude, longitude, height, Q):
    """
    This function will calculate the standard deviation between the points.
    
    Input:  latitude <list><float> - Latitude of position
            longitude <list><float> - Longitude of positon
            height <list><float> - Height of position
            Q <list><int> - Signal quality

    Output: sigma <float> - Standard deviation of data
            meanDistance <float> - Mean of dataset
            distaneList <list><float> - list of distances
            distaneListENU <list> - ENU Positions
    """
    # Calculate average position per data
    latitudeQ1 = []
    longitudeQ1 = []
    heightQ1 = []
    for index in range(len(latitude)):

        # Check if Q is 1
        if Q[index] == 1:

            # Pull data
            latitudeQ1.append(latitude[index])
            longitudeQ1.append(longitude[index])
            heightQ1.append(height[index])
            
    # Calculate average position
    averagePosition = [mean(latitudeQ1), mean(longitudeQ1), mean(heightQ1)]

    # Calculate ENU coordinates for error
    distaneListENU = []
    for index in range(len(latitude)):

        # Check if Q is 1
        if Q[index] == 1:

            # Calculate ENU data
            ENUCoord = geodetic2enu(latitude[index],longitude[index],height[index],averagePosition[0],averagePosition[1],averagePosition[2])
            distaneListENU.append(ENUCoord)

    return distaneListENU



if __name__ == "__main__":
    main()