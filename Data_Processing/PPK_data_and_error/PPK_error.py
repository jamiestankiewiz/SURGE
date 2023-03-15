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
    distanceListEast = np.array([distanceENU[0] for distanceENU in distaneListENU[0]])*convertToMeters
    distanceListNorth = np.array([distanceENU[1] for distanceENU in distaneListENU[0]])*convertToMeters
    distanceListUp = np.array([distanceENU[2] for distanceENU in distaneListENU[0]])*convertToMeters

    # Pull std values
    sigma_EN = distaneListENU[1]*convertToMeters
    sigma_EU = distaneListENU[2]*convertToMeters
    sigma_NU = distaneListENU[3]*convertToMeters

    # Pull distance values
    distanceEN = np.array(distaneListENU[4])*convertToMeters
    distanceEU = np.array(distaneListENU[5])*convertToMeters
    distanceNU = np.array(distaneListENU[6])*convertToMeters

    # Create circles for EN
    theta = np.linspace( 0 , 2 * np.pi , 150 )
    a_one_sigma_EN = sigma_EN * np.cos(theta)
    a_two_sigma_EN = 2*sigma_EN * np.cos(theta)
    a_three_sigma_EN = 3*sigma_EN * np.cos(theta)
    b_one_sigma_EN = sigma_EN * np.sin(theta)
    b_two_sigma_EN = 2*sigma_EN * np.sin(theta)
    b_three_sigma_EN = 3*sigma_EN * np.sin(theta)

    # Create scatter plot
    fig, axs = plt.subplots(2,2)
    axs[0, 0].grid(color='k', linestyle='--', linewidth=0.3)
    axs[0, 0].scatter(distanceListEast, distanceListNorth)
    axs[0, 0].set_title('EN Error')
    axs[0, 0].plot( a_one_sigma_EN, b_one_sigma_EN, "r", label = "One Sigma" )
    axs[0, 0].plot( a_two_sigma_EN, b_two_sigma_EN, "g", label = "Two Sigma" )
    axs[0, 0].plot( a_three_sigma_EN, b_three_sigma_EN, "y", label = "Three Sigma" )
    axs[0, 0].legend(loc="upper right")
    axs[0, 0].axis('equal')

    # Create circles for EU
    a_one_sigma_EU = sigma_EU * np.cos(theta)
    a_two_sigma_EU = 2*sigma_EU * np.cos(theta)
    a_three_sigma_EU = 3*sigma_EU * np.cos(theta)
    b_one_sigma_EU = sigma_EU * np.sin(theta)
    b_two_sigma_EU = 2*sigma_EU * np.sin(theta)
    b_three_sigma_EU = 3*sigma_EU * np.sin(theta)

    # Create scatter plot
    axs[0, 1].grid(color='k', linestyle='--', linewidth=0.3)
    axs[0, 1].scatter(distanceListEast, distanceListUp)
    axs[0, 1].set_title('EU Error')
    axs[0, 1].plot( a_one_sigma_EU, b_one_sigma_EU, "r", label = "One Sigma" )
    axs[0, 1].plot( a_two_sigma_EU, b_two_sigma_EU, "g", label = "Two Sigma" )
    axs[0, 1].plot( a_three_sigma_EU, b_three_sigma_EU, "y", label = "Three Sigma" )
    axs[0, 1].legend(loc="upper right")
    axs[0, 1].axis('equal')

    # Create circles for EU
    a_one_sigma_NU = sigma_NU * np.cos(theta)
    a_two_sigma_NU = 2*sigma_NU * np.cos(theta)
    a_three_sigma_NU = 3*sigma_NU * np.cos(theta)
    b_one_sigma_NU = sigma_NU * np.sin(theta)
    b_two_sigma_NU = 2*sigma_NU * np.sin(theta)
    b_three_sigma_NU = 3*sigma_NU * np.sin(theta)

    # Create scatter plot
    axs[1, 0].grid(color='k', linestyle='--', linewidth=0.3)
    axs[1, 0].scatter(distanceListNorth, distanceListUp)
    axs[1, 0].set_title('NU Error')
    axs[1, 0].plot( a_one_sigma_NU, b_one_sigma_NU, "r", label = "One Sigma" )
    axs[1, 0].plot( a_two_sigma_NU, b_two_sigma_NU, "g", label = "Two Sigma" )
    axs[1, 0].plot( a_three_sigma_NU, b_three_sigma_NU, "y", label = "Three Sigma" )
    axs[1, 0].legend(loc="upper right")
    axs[1, 0].axis('equal')

    # Remove extra plot
    axs[1,1].set_axis_off()

    # Set plot labels
    for ax in axs.flat[2:]:
        ax.set(xlabel='Error [cm]')
    for ax in [axs.flat[0], axs.flat[2]]:
        ax.set(ylabel='Error [cm]')

    # Plot histogram distance values
    fig, axs = plt.subplots(2,2)
    axs[0, 0].grid(color='k', linestyle='--', linewidth=0.3)
    axs[0, 0].hist(distanceEN, 150)
    axs[0, 0].set_title('EN Error')
    axs[0, 0].axvline( sigma_EN, color = "r", label = "One Sigma" )
    axs[0, 0].axvline( 2*sigma_EN, color = "g", label = "Two Sigma" )
    axs[0, 0].axvline( 3*sigma_EN, color = "y", label = "Three Sigma" )
    axs[0, 0].legend(loc="upper right")

    # Create scatter plot
    axs[0, 1].grid(color='k', linestyle='--', linewidth=0.3)
    axs[0, 1].hist(distanceEU, 150)
    axs[0, 1].set_title('EU Error')
    axs[0, 1].axvline( sigma_EU, color = "r", label = "One Sigma" )
    axs[0, 1].axvline( 2*sigma_EU, color = "g", label = "Two Sigma" )
    axs[0, 1].axvline( 3*sigma_EU, color = "y", label = "Three Sigma" )
    axs[0, 1].legend(loc="upper right")

    # Create scatter plot
    axs[1, 0].grid(color='k', linestyle='--', linewidth=0.3)
    axs[1, 0].hist(distanceNU, 150)
    axs[1, 0].set_title('NU Error')
    axs[1, 0].axvline( sigma_NU, color = "r", label = "One Sigma" )
    axs[1, 0].axvline( 2*sigma_NU, color = "g", label = "Two Sigma" )
    axs[1, 0].axvline( 3*sigma_NU, color = "y", label = "Three Sigma" )
    axs[1, 0].legend(loc="upper right")

    # Set plot labels
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
    distanceEU = []
    distanceNU = []
    for index in range(len(coordListENU)):
        
        # Calculate point and distane values
        distanceEN.append(sqrt(pow(coordListENU[index][0],2) + pow(coordListENU[index][1],2)))
        distanceEU.append(sqrt(pow(coordListENU[index][0],2) + pow(coordListENU[index][2],2)))
        distanceNU.append(sqrt(pow(coordListENU[index][1],2) + pow(coordListENU[index][2],2)))

    # Calculate distance ranges sigma
    sigmaEN = np.std(distanceEN)
    sigmaEU = np.std(distanceEU)
    sigmaNU = np.std(distanceNU)

    # Combine to array
    distaneListENU = [coordListENU, sigmaEN, sigmaEU, sigmaNU, distanceEN, distanceEU, distanceNU]

    return distaneListENU



if __name__ == "__main__":
    main()