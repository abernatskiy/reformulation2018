'''Module containing definitions that are exclusively useful in the gigantic convergence research program'''

import numpy as np
from os.path import join

# Functions for studying the distance from the maximally modular morphology (MMM)

def _hammingDistance(first, second):
	'''Computes a Hamming distance between two numeric arrays'''
	return sum(np.abs(first-second))

def _maximallyModularMorpohlogy(segments):
	'''Generates a genome for maximally modular morphology'''
	return np.array(range(1, segments+1))

def _hammingDistanceToMMM(morphology):
	return _hammingDistance(morphology, _maximallyModularMorpohlogy(len(morphology)))

def hammingDistancesAndFitnessFromParetoFrontFile(genNum, dataFolder='.'):
	'''Returns three arrays: individual IDs, their corresponding fitnesses and how far their morphologies are from the MMM'''
	filename = join(dataFolder, 'paretoFront_gen{}.log'.format(genNum))
	contents = np.loadtxt(filename, ndmin=2)
	ids = np.array(contents[:,1], dtype=np.int)
	fitness = np.array(contents[:,0], dtype=np.float)
	morphologies = np.array(contents[:,2:5], dtype=np.int)
	mmmDists = np.apply_along_axis(_hammingDistanceToMMM, axis=1, arr=morphologies)
	return ids, fitness, mmmDists

def minParetoFrontHammingDistanceToMMM(genNum, dataFolder='.'):
	_, _, mmmDists = hammingDistancesAndFitnessFromParetoFrontFile(genNum)
	return min(mmmDists)
