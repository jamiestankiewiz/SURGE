from write1 import write_count_up
from write2 import write_count_down

def write_to_SSD(test_filename, path_to_SSD):
    with open(test_filename, 'w') as file:
        write_count_up(path_to_SSD)

if __name__ == '__main__':
    write_to_SSD(test_filename='test_file.txt', path_to_SSD='/media/DataStore/usrp3')
