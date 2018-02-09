#!/usr/bin/python2

import numpy as np

# compute sums of values written into the ouput pipe of the evolution,
# scale it to fit into [0,1] and write the result into the input pipe 
# of the evolution

fnindivs = 'individuals.pipe'
fnevals = 'evaluations.pipe'

while True:
	indivs = np.loadtxt(fnindivs)
	ids = np.array(indivs[:,0], dtype=np.int64)
	rawEvals = np.sum(indivs[:,1:], 1)
	maxsc = max(rawEvals)
	minsc = min(rawEvals)
	normalize = np.vectorize(lambda x: 1.0 if minsc == maxsc else (x - minsc)/(maxsc - minsc))
#	evals = normalize(rawEvals)
	evals = rawEvals
	fevals = open(fnevals, 'w')
	for i in xrange(len(ids)):
		fevals.write(str(ids[i]) + ' ' + str(evals[i]) + '\n')
	fevals.close()
