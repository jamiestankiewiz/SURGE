from multiprocessing import Process, cpu_count
# from threading import Thread
from count_up import count_up
from count_down import count_down
# import concurrent.futures

if __name__ == '__main__':
    print('cores: ', cpu_count())
    processes = []
    p1 = Process(target=count_up)
    p2 = Process(target=count_down)

    p1.start()
    print('p1 start')
    p2.start()
    print('p2 start')
    for p in (p1, p2):
        p.join()
    # processes = [p.join() for p in (p1, p2)]

    # with concurrent.futures.ProcessPoolExecutor() as executor:
    #     process1 = executor.submit(count_up)
    #     process2 = executor.submit(count_down)
    print('finished')
