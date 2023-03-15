"""
    INPUTS:
        file: name of sc8 data file (in /media/DataStore/usrp3),
        start time: number in minutes/seconds,
        stop time: number in minutes/seconds,
        sampling_freq: 22e6 [bits/second] from the b210_split_settings-balloon.xml file
    OUTPUT:
        truncated sc8 data file
    t=0 at start of file
    write out a data file
"""

file = '~/media/DataStore/usrp3/20230313_boulderreservoir_test1/20230313_094235_000000_BALLOON_1176.45_22.0.sc8'

def main(file, start_time, end_time, sampling_freq=22e6):
    pass

if __name__=="__main__":
    file_chunk = main(file=file, start_time=0, end_time=0)
