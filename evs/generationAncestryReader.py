#!/usr/bin/python2

import cPickle
import sys

with open(sys.argv[1]) as f:
	evolver = cPickle.load(f)

for indiv in evolver.population:
	print 'Individual: ' + str(indiv)
	print 'Ancestry: ' + str(indiv.ancestry)
	print
