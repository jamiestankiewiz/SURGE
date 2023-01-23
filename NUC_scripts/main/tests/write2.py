from datetime import datetime

def write_count_down(filename):
    '''write to a file: file2.txt'''
    with open(filename, 'w') as file:
        file.write('This test started on: ' + str(datetime.now()) + '\n')
        for i in range(100, 0, -1):
            file.write(str(i) + '\n')
        file.write('This test concluded on: ' + str(datetime.now()))

if __name__ == '__main__':
    write_count_down(filename='Desktop/Code/SURGE/NUC_scripts/main/tests/file2.txt')
