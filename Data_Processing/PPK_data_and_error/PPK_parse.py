from dateutil import tz
from lib.parse_pos_data import ParsePOSData
from datetime import datetime
from navpy import lla2ecef

def main():
    """
    Parse PPK data file (.pos)
    """
    # Enter file name
    fileName = 'PPKdata_39_2023-03-13-09_42_10.pos'

    # Find path to file
    currentFile = str(__file__).split('\\')
    currentFile = currentFile[:-1]
    currentFile = '\\'.join(currentFile)
    fileName = currentFile + '\data_files\\' + fileName

    # Define file object
    errorFile = ParsePOSData(fileName)

    # Pull file data
    GPST, latitude, longitude, height, Q, _ = errorFile.getPOSData()

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
    drone_ecef = lla2ecef(lat=latitude, lon=longitude, alt=height, latlon_unit='deg', alt_unit='m',
             model='wgs84')
    print(drone_ecef)


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
    timeValue = [datetime.strptime(date_time, '%Y/%m/%d %H:%M:%S.%f') for date_time in timeValueCombine]
            
    # Tell the datetime object that it's in UTC time zone since 
    # datetime objects are 'naive' by default
    timeValue = [date_time.replace(tzinfo=fromZone) for date_time in timeValue] # UTC

    # Convert time zone
    MST = [date_time.astimezone(toZone) for date_time in timeValue]

    return MST

if __name__=='__main__':
    main()
