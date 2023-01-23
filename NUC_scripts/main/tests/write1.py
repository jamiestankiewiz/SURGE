from datetime import datetime

def write_count_up(filename):
    '''write to a file named file1.txt'''
    with open(filename, 'w') as file:
        file.write('This test started on: ' + str(datetime.now()) + '\n')
        for i in range(100):
            file.write(str(i) + '\n')
            i += 1
        file.write('This test concluded on: ' +  str(datetime.now()))

if __name__ == '__main__':
    write_count_up(filename='Desktop/Code/SURGE/NUC_scripts/main/tests/file1.txt')
