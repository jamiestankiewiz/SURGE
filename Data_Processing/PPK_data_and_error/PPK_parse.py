from dateutil import tz
from lib.parse_pos_data import ParsePOSData
from datetime import datetime
from navpy import lla2ecef
import numpy as np
from scipy import optimize
import csv

def main(fileName, satellite_ecef):
    """
    Parse PPK data file (.pos)
    """
    # Find path to file
    currentFile = str(__file__).split('\\')
    currentFile = currentFile[:-1]
    currentFile = '\\'.join(currentFile)
    fileName = currentFile + '\data_files\\' + fileName

    # Define file object
    errorFile = ParsePOSData(fileName)

    # Pull file data
    GPST, latitude, longitude, height, Q, _ = errorFile.getPOSData()

    # Altitude of Boulder res [m]
    boulder_alt = 1578

    # Print values
    # print(GPST) # GPS_time/UTC, parse this, convert to datetime
    # print('latitude', latitude) # [degrees]
    # print('longitude', longitude) # [degrees]
    # print('height', height) # SL reference, [m]
    # print('Q', Q) # data quality

    # Convert time to MST
    MST = convertUTCtoMST(GPST=GPST)

    # Convert height (wrt SL) to altitude above Boulder Res
    # Boulder Res altitude: 1578 m
    # altitude = 1578 # m
    # height = [alt - altitude for alt in height]
    # if any([alt <=0 for alt in height]):
    #     print('INVALID ALTITUDE: altitude less than Boulder altitude.')

    # Positional location of drone
    drone_ecef = lla2ecef(lat=latitude, lon=longitude, alt=height,
                          latlon_unit='deg', alt_unit='m',
                          model='wgs84')
    print('length of drone ecef', len(drone_ecef))
    flighttime_75percent = drone_ecef[int(len(drone_ecef)*.75)]
    print('75 percent into flight', flighttime_75percent)


    with open('drone_ecef', 'w') as f:
        # using csv.writer method from CSV package
        write = csv.writer(f)
        for drone_ecef_point in drone_ecef:
            write.writerow(drone_ecef_point)

    # note: incorportate boulder alt of 1578 m
    spCalc = lambda x: np.linalg.norm(x - satellite_ecef) + \
                       np.linalg.norm(x - flighttime_75percent)
    xopt = optimize.fmin(func=spCalc, x0=flighttime_75percent)
    print('Optimized SP', xopt)

    # drone height at 75% into flight
    # TODO: really convert this based on time
    print('Height of drone [m]', height[int(.75*len(height))] - boulder_alt)


def convertUTCtoMST(GPST):
    """
    PPK data is in UTC, change to MST.
    Input:
        GPST <list><str> - Time data (in UTC)
    Output:
        # currently datetime objects
        GPST <list><str> - Time data (in MST)
    """
    fromZone = tz.gettz('UTC')
    toZone = tz.gettz('America/Denver')

    timeValueCombine = [date + ' ' + time for date, time in GPST]    
    timeValue = [datetime.strptime(date_time, '%Y/%m/%d %H:%M:%S.%f')
                 for date_time in timeValueCombine]

    # Tell the datetime object that it's in UTC time zone since 
    # datetime objects are 'naive' by default
    timeValue = [date_time.replace(tzinfo=fromZone) for date_time in timeValue] # UTC

    # Convert time zone
    MST = [date_time.astimezone(toZone) for date_time in timeValue]

    return MST

if __name__=='__main__':
    main(fileName = 'PPKdata_39_2023-03-13-09_42_10.pos',
         satellite_ecef = [16163520.8974696, -9843045.49135850, -18726663.2253074]
         )
