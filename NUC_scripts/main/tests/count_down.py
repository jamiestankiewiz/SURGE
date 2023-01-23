from time import sleep

def count_down():
    i = 100
    while True:
        print(i)
        sleep(1)
        i -= 1

# count_down()
