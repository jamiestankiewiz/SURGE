import os

def main(file, start_time, end_time, sampling_freq=22e6):
    """
    Truncate a file based on start and stop time.
    INPUTS:
        file: name of sc8 data file (in /media/DataStore/usrp3),
        start time: number in minutes or seconds,
        stop time: number in minutes or seconds,
        sampling_freq: 22e6 [bits?/second] from the b210_split_settings-balloon.xml file
    OUTPUT:
        truncated sc8 data file
    t=0 at start of file
    """
    pass

if __name__=="__main__":
    # file = '~/media/DataStore/usrp3/20230313_boulderreservoir_test1/20230313_094235_000000_BALLOON_1176.45_22.0.sc8'
    file = '../../NUC_scripts/SDR_backup_files/test_sc8_files/20230201_210903_000001_BALLOON_1176.45_22.0.sc8'
    start_time = os.path.getctime(file) # seconds
    last_modified = os.path.getmtime(file) # seconds
    size = os.path.getsize(file) # bytes
    file_chunk = main(file=file, start_time=start_time, end_time=last_modified)
    print('file_time difference', last_modified-start_time, 'seconds')
    print(size/10**6, 'Mb')
