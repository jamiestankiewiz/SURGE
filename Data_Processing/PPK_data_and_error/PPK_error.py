#!/usr/bin/env python3

"""
Author: Andreas Brecl
Date: 03/08/2023

This script will calculate the PPK error bounds.
"""

from lib.parse_pos_data import ParsePOSData
from statistics import mean
from geopy import distance
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
    meanDistance, sigma, distaneList = calculateSigmaAndMean(latitude, longitude, height, Q)
    print(meanDistance)
    print(sigma)

    # Plot values
    plotErrorValues(meanDistance, sigma, distaneList)

def plotErrorValues(meanDistance, sigma, distaneList):
    """
    This function will plot the resulting values form the error calculations.

    Inupt:  sigma <float> - Standard deviation of data
            meanDistance <float> - Mean of dataset
            distaneList <list><float> - list of distances

    Output: None
    """
    # Convert to numpy array
    distaneListNp = np.array(distaneList)

    # Create histogram
    plt.hist(distaneListNp, 200)
    plt.xlabel("Distance [cm]")
    plt.ylabel("Number of Occurances")
    plt.title("Distance from Calculated Average Value")
    plt.axvline(sigma, color='k', linestyle='dashed', linewidth=1)

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

    # Calculate distance between points
    distaneList = []
    for index in range(len(latitude)):

        # Check if Q is 1
        if Q[index] == 1:

            # Calculate GNSS distance difference to meters
            averageGpsPosition = (averagePosition[0], averagePosition[1])
            gpsPosition = (latitude[index], longitude[index])
            gpsDistance = distance.distance(averageGpsPosition, gpsPosition).km*1000
            heightPosition = abs(averagePosition[2] - height[index])

            # Calculate distance
            currentDistance = sqrt(pow(gpsDistance,2) + pow(heightPosition,2))*100
            distaneList.append(currentDistance)

    # Calculate standard deviation
    sigma = np.std(distaneList)
    meanDistance = mean(distaneList)

    return meanDistance, sigma, distaneList



if __name__ == "__main__":
    main()