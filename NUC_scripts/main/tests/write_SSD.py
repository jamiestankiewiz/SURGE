from write1 import write_count_up
from write2 import write_count_down
from multiprocessing import Process
from time import sleep
import sys
sys.path.append("..")
from lib.disk_usage_monitor import DiskUsageMonitor

def write_to_SSD(test_filename, path_to_SSD):
    write_count_up(path_to_SSD + test_filename)

def print_disk_status():
    disk_status = DiskUsageMonitor(pathToDisk='/media/DataStore/test')
    while True:
        print(disk_status.isDiskWriting())

if __name__ == '__main__':
    p1 = Process(target=write_to_SSD, args=('test_file.txt', '/media/DataStore/test'))
    p2 = Process(target=print_disk_status)
    p2.start()
    sleep(1)
    p1.start()

