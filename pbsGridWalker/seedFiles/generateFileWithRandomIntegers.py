#!/usr/bin/python2

import sys

if len(sys.argv) > 3:
	print('Usage: generateFileWithRandomIntegers.py [ howMany [ upperLimit ] ]')
	sys.exit()

howMany = 100

if len(sys.argv) > 1:
	howMany = int(sys.argv[1])

upperLimit = 10000

if len(sys.argv) > 2:
	upperLimit = int(sys.argv[2])

if howMany > upperLimit:
	print('Cannot uniquify integers, exiting')
	sys.exit()

import numpy as np
import time

t = int(time.time())
filename = 'randints' + str(t) + '.dat'

arr = np.arange(upperLimit)
np.random.shuffle(arr)
np.savetxt(filename, arr[:howMany], fmt='%u')

print('Wrote file ' + filename)
