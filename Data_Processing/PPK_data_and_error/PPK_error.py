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
    # Define constants
    convertToMeters = 100

    # Convert ENU values to numpy array
    distanceE = np.array(distaneListENU[5])*convertToMeters
    distanceN = np.array(distaneListENU[6])*convertToMeters
    distanceU = np.array(distaneListENU[7])*convertToMeters

    # Pull std values
    sigma_EN = distaneListENU[1]*convertToMeters
    sigma_E = distaneListENU[2]*convertToMeters
    sigma_N = distaneListENU[3]*convertToMeters
    sigma_U = distaneListENU[4]*convertToMeters

    # Create circles for EN
    theta = np.linspace( 0 , 2 * np.pi , 150 )
    a_one_sigma_EN = sigma_EN * np.cos(theta)
    a_two_sigma_EN = 2*sigma_EN * np.cos(theta)
    a_three_sigma_EN = 3*sigma_EN * np.cos(theta)
    b_one_sigma_EN = sigma_EN * np.sin(theta)
    b_two_sigma_EN = 2*sigma_EN * np.sin(theta)
    b_three_sigma_EN = 3*sigma_EN * np.sin(theta)

    # Create scatter plot
    fig, axs = plt.subplots(1,2)
    axs[0].grid(color='k', linestyle='--', linewidth=0.3)
    axs[0].scatter(distanceE, distanceN, marker = ".")
    axs[0].set_title('EN Error')
    axs[0].plot( a_one_sigma_EN, b_one_sigma_EN, "r--", label = "$\sigma$" )
    axs[0].plot( a_two_sigma_EN, b_two_sigma_EN, "g--", label = "2$\sigma$" )
    axs[0].plot( a_three_sigma_EN, b_three_sigma_EN, "y--", label = "3$\sigma$" )
    axs[0].legend(loc="upper right")
    axs[0].axis('equal')

    # Create plot
    axs[1].grid(color='k', linestyle='--', linewidth=0.3)
    axs[1].set_title('ENU Error')
    axs[1].plot( np.linspace(1, distanceN.size+1, num=distanceN.size), distanceN, "b", linestyle = "none", marker = ".", label = "N Error" )
    axs[1].plot( np.linspace(1, distanceU.size+1, num=distanceU.size), distanceU, "r", linestyle = "none", marker = ".", label = "U Errorr" )
    axs[1].plot( np.linspace(1, distanceE.size+1, num=distanceE.size), distanceE, "g", linestyle = "none", marker = ".", label = "E Error" )
    axs[1].legend(loc="upper right")

    # Set plot labels
    axs.flat[0].set(xlabel='Error [cm]')
    axs.flat[1].set(xlabel='Time [sec]')
    for ax in [axs.flat[0], axs.flat[1]]:
        ax.set(ylabel='Error [cm]')

    # Plot histogram distance values
    fig, axs = plt.subplots(2,2)
    axs[0, 0].grid(color='k', linestyle='--', linewidth=0.3)
    axs[0, 0].hist(distanceE, 150)
    axs[0, 0].set_title('E Error')
    axs[0, 0].axvline( sigma_E, color = "r", linestyle='--', label = "$\sigma$" )
    axs[0, 0].axvline( 2*sigma_E, color = "g", linestyle='--', label = "2$\sigma$" )
    axs[0, 0].axvline( 3*sigma_E, color = "y", linestyle='--', label = "3$\sigma$" )
    axs[0, 0].axvline( -sigma_E, color = "r", linestyle='--')
    axs[0, 0].axvline( -2*sigma_E, color = "g", linestyle='--')
    axs[0, 0].axvline( -3*sigma_E, color = "y", linestyle='--')
    axs[0, 0].legend(loc="upper right")

    # Create scatter plot
    axs[0, 1].grid(color='k', linestyle='--', linewidth=0.3)
    axs[0, 1].hist(distanceN, 150)
    axs[0, 1].set_title('N Error')
    axs[0, 1].axvline( sigma_N, color = "r", linestyle='--', label = "$\sigma$" )
    axs[0, 1].axvline( 2*sigma_N, color = "g", linestyle='--', label = "2$\sigma$" )
    axs[0, 1].axvline( 3*sigma_N, color = "y", linestyle='--', label = "3$\sigma$" )
    axs[0, 1].axvline( -sigma_N, color = "r", linestyle='--')
    axs[0, 1].axvline( -2*sigma_N, color = "g", linestyle='--')
    axs[0, 1].axvline( -3*sigma_N, color = "y", linestyle='--')
    axs[0, 1].legend(loc="upper right")

    # Create scatter plot
    axs[1, 0].grid(color='k', linestyle='--', linewidth=0.3)
    axs[1, 0].hist(distanceU, 150)
    axs[1, 0].set_title('U Error')
    axs[1, 0].axvline( sigma_U, color = "r", linestyle='--', label = "$\sigma$" )
    axs[1, 0].axvline( 2*sigma_U, color = "g", linestyle='--', label = "2$\sigma$" )
    axs[1, 0].axvline( 3*sigma_U, color = "y", linestyle='--', label = "3$\sigma$" )
    axs[1, 0].axvline( -sigma_U, color = "r", linestyle='--')
    axs[1, 0].axvline( -2*sigma_U, color = "g", linestyle='--')
    axs[1, 0].axvline( -3*sigma_U, color = "y", linestyle='--')
    axs[1, 0].legend(loc="upper right")

    # Set plot labels
    axs.flat[1].set(xlabel='Error [cm]')
    for ax in axs.flat[2:]:
        ax.set(xlabel='Error [cm]')
    for ax in [axs.flat[0], axs.flat[2]]:
        ax.set(ylabel='Number of Occurances')

    # Remove extra plot
    axs[1,1].set_axis_off()

    # Show plot
    plt.show()

def calculateSigmaAndMean(latitude, longitude, height, Q):
    """
    This function will calculate the standard deviation between the points.
    
    Input:  latitude <list><float> - Latitude of position
            longitude <list><float> - Longitude of positon
            height <list><float> - Height of position
            Q <list><int> - Signal quality

    Output: distaneListENU <list> - ENU Positions and sigma values
    """
    # Define constants
    convertToMeters = 100

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
    coordListENU = []
    for index in range(len(latitude)):

        # Check if Q is 1
        if Q[index] == 1:

            # Calculate ENU data
            ENUCoord = geodetic2enu(latitude[index],longitude[index],height[index],averagePosition[0],averagePosition[1],averagePosition[2])
            coordListENU.append(ENUCoord)

    # Calculate distance between points
    distaneListENU = []
    distanceEN = []
    distanceE = []
    distanceN = []
    distanceU = []
    for index in range(len(coordListENU)):
        
        # Calculate point and distane values
        distanceEN.append(sqrt(pow(coordListENU[index][0],2) + pow(coordListENU[index][1],2)))
        distanceE.append(coordListENU[index][0])
        distanceN.append(coordListENU[index][1])
        distanceU.append(coordListENU[index][2])

    # Calculate distance ranges sigma
    sigmaEN = np.std(distanceEN)
    sigmaE = np.std(distanceE)
    sigmaN = np.std(distanceN)
    sigmaU = np.std(distanceU)

    # Combine to array
    distaneListENU = [coordListENU, sigmaEN, sigmaE, sigmaN, sigmaU, distanceE, distanceN, distanceU]

    return distaneListENU



if __name__ == "__main__":
    main()