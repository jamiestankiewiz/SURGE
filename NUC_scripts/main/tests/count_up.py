from itertools import count
from time import sleep

def count_up():
    i = 0
    while True:
        print(i)
        sleep(1)
        i += 1

# count_up()