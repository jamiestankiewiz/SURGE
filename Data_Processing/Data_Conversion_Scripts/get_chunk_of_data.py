import os
import fmmap as mmap

def main(file, start_time, stop_time, sampling_freq=22e6):
    """
    Truncate a file based on start and stop time.
    INPUTS:
        file: name of sc8 data file (in /media/DataStore/usrp3),
        start time: int [seconds],
        stop time: int [seconds],
        sampling_freq: 22e6 [bits/second] from the b210_split_settings-balloon.xml file
    OUTPUT:
        truncated sc8 data file
    t=0 at start of file
    """
    start_bit = int(sampling_freq*start_time)
    stop_bit = int(sampling_freq*stop_time)
    with open(file, 'rb') as f:
        # memory-map the file, size 0 means whole file
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)

        NEW_FILE_NAME = 'trunc_' + file.split('/')[-1]

        NEW_FILE_SIZE = stop_bit - start_bit + 1
        new_f = open(NEW_FILE_NAME, "wb")
        new_f.write((NEW_FILE_SIZE)*b'\0')
        new_f.close()
        
        with open(NEW_FILE_NAME, "r+b") as new_file_obj:
            # export/write sliced mmap object
            with mmap.mmap(new_file_obj.fileno(), length=0, access=mmap.ACCESS_WRITE) as mmap_obj:
                mmap_obj.write(mm[start_bit:stop_bit])
        # close the map
        mm.close()


if __name__=="__main__":
    # file = '~/media/DataStore/usrp3/20230313_boulderreservoir_test1/20230313_094235_000000_BALLOON_1176.45_22.0.sc8'
    file = '../../NUC_scripts/SDR_backup_files/test_sc8_files/20230202_191216_000001_BALLOON_1176.45_22.0.sc8'
    # File information
    file_creation_time = os.path.getctime(file) # seconds
    last_modified = os.path.getmtime(file) # seconds
    size = os.path.getsize(file) # bytes
    # User input
    start_time = 1
    stop_time = 1.001
    
    print('file_time difference', last_modified-start_time, 'seconds')
    print(size/10**6, 'Mb')

    file_chunk = main(file=file, start_time=start_time, stop_time=stop_time)
