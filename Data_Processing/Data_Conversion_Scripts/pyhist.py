#!/usr/bin/env python3

import sys

import numpy as np
import matplotlib.pyplot as pp
import csv

# Test file /media/DataStore/usrp3/20230313_boulderreservoir_test1/20230313_094235_000000_BALLOON_1176.45_22.0.sc8

x = np.fromfile(sys.argv[1], dtype=np.int8, count=100000)

data=x[0:-2:2]+1j*x[1: -1 :2]

#print(type(data))
data.tofile("Output.csv",sep=',')
with open("Output.csv",'w') as file:
    write = csv.writer(file,delimiter=',')
    write.writerow(x)

pp.hist(x, bins=16)
pp.saveplot('image.png')
