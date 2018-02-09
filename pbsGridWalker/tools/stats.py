import numpy as np

import algorithms

def stderr(samples):
	return np.std(samples)/np.sqrt(float(len(samples)))

def timeSeriesStderr(samples):
	'''Each row is a sample trajectory'''
	return np.std(samples, axis=0)/np.sqrt(float(samples.shape[0]))

def chunkedMaxStats(fitness, numChunks):
	if len(fitness[0]) % numChunks != 0:
		raise ValueError('Number of fitness records (' + str(len(fitness[0])) + ')  must be divisible by the number of chunks (' + str(numChunks) + ')')
	lenChunk = len(fitness[0])/numChunks
	fitChunks = algorithms.chunks(fitness[0], lenChunk)
	fitMax = map(np.max, fitChunks)
	return (np.mean(fitMax), np.std(fitMax))
