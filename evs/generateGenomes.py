#!/usr/bin/python2

from individuals.trinaryVectorSureMutation import Individual
from communicators.textFileOutputOnly import Communicator
from evolvers.proportionalEvolver import Evolver

import sys

if len(sys.argv) != 5:
	print 'Usage: generateGenomes.py <randomSeed> <sampleSize> <outputFilename> <length>'
	sys.exit(1)

try:
	randseed = int(sys.argv[1])
	popsize = int(sys.argv[2])
	lngth = int(sys.argv[4])
except ValueError:
	print 'Usage: generateGenomes.py <randomSeed> <sampleSize> <outputFilename> <length>'
	sys.exit(1)

indivParams = {'length': lngth}
evolParams = {'indivClass': Individual, \
              'populationSize': popsize, \
              'randomSeed': randseed}

comm = Communicator('evaluations.txt', sys.argv[3])

evolver = Evolver(comm, indivParams, evolParams)
