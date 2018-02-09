#!/usr/bin/python2

import os
import numpy as np
import subprocess

import staticEvsDynamicCeExperiment as sedce
from shared.grid import LogGrid,Grid1d
from uniformSamplingLPE import baseGrid

class runLPEExperiment(sedce.staticEvsDynamicCeExperiment):
	def processResults(self):
		pass

	def evsConfig(self):
		return ('[classes]\n'
						'individual = trinaryVectorSureMutation\n'
						'communicator = chunkedUnixPipe\n'
						'evolver = proportionalEvolver\n'
						'\n'
						'[indivParams]\n'
						'length = 60\n'
						'\n'
						'[evolParams]\n'
						'populationSize = 10\n'
						'eliteSize = 1\n'
						'logBestIndividual = yes\n'
						'genStopAfter = 10\n')

def initializeExperiment():
	grid = baseGrid()
	grid += Grid1d('randomSeeds', [[9001, 9002, 9003]]*len(grid))
	return runLPEExperiment('runLPE20151115',
					[{'linearDrag':0.0, 'angularDrag':0.0}, {'linearDrag':0.2, 'angularDrag':0.2}],
					grid=grid,
					pointsPerJob=2,
#					dryRun=True,
					expectedWallClockTime='00:30:00')

if __name__ == '__main__':
	e = initializeExperiment()
	e.run()
