#!/usr/bin/python2

from os.path import expanduser
import sys

home = expanduser("~")
file = open(home + '/pbsGridWalker/seedFiles/randints1421128240.dat', 'r')
seeds = []
for line in file:
  seeds.append(int(line))

requestedSeeds = []
for i in range(1, len(sys.argv)):
	requestedSeeds.append(seeds[int(sys.argv[i])])

for seed in requestedSeeds:
	print seed
