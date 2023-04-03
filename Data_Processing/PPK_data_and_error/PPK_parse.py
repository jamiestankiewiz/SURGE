from dateutil import tz
from lib.parse_pos_data import ParsePOSData
from datetime import datetime


def main():
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
    MST = convertUTCtoMST(GPST=GPST)
    print(MST)


def convertUTCtoMST(GPST):
    """
    Input:
        GPST <list><str> - Time data (in UTC)
    Output:
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