#!/usr/bin/python2

import os
import numpy as np
import subprocess

import staticEvsDynamicCeExperiment as sedce
from shared.grid import LogGrid,Grid1d

import tools.fileProcessors as tfp
import tools.stats as ts
import tools.algorithms as ta

def extractFitness(filename):
	return np.array(tfp.extractColumnFromEVSLogs(filename, 1))

class uniformSamplingLPEExperiment(sedce.staticEvsDynamicCeExperiment):
	def processResults(self):
		def processDir(gridPoint, condPoint, self):
			fileNameBase = 'population' + str(int(gridPoint['randomSeeds'])) + '_gen'
			files = [ fileNameBase + '0.log', fileNameBase + '1.log' ]
			fitness = [ extractFitness(file) for file in files ]
			fullCond = ta.sumOfDicts(gridPoint, condPoint)

			self._recordEvolvabilityStats(fullCond, fitness)
			self._recordRandomSearchStats(fullCond, fitness)

		self.executeAtEveryConditionsDir(processDir, (self,), {})

	def _recordRandomSearchStats(self, fullCond, fitness):
		results = {}
		for nc in [1, 10, 100, 1000]:
			mean, std = ts.chunkedMaxStats(fitness, nc)
			results['mean' + str(nc)] = mean
			results['std' + str(nc)] = std
		self.addResultRecord('randomSearchStats.dat', fullCond, results)

	def _recordEvolvabilityStats(self, fullCond, fitness):
		inc = (fitness[1] - fitness[0])/fitness[0]
		diff = np.abs(fitness[1] - fitness[0])/fitness[0]

		results = {}
		results['incMean'] = np.mean(inc)
		results['incStdErr'] = ts.stderr(inc)
		self.addResultRecord('increments.dat', fullCond, results)

		results = {}
		results['diffMean'] = np.mean(diff)
		results['diffStdErr'] = ts.stderr(diff)
		self.addResultRecord('differences.dat', fullCond, results)

	def evsConfig(self):
		return ('[classes]\n'
						'individual = trinaryVectorSureMutation\n'
						'communicator = chunkedUnixPipe\n'
						'evolver = evolvabilityMeasurerUniformSampling\n'
						'\n'
						'[indivParams]\n'
						'length = 60\n'
						'\n'
						'[evolParams]\n'
						'populationSize = 1000\n'
						'logPopulation = yes\n')

def baseGrid():
	sgGrid = LogGrid('sensorGain', 16, 4, 1, 1)
	fgGrid = LogGrid('forceGain', 0.8, 4, 2, 2)
	return sgGrid*fgGrid

def initializeExperiment():
	grid = baseGrid()
	grid += Grid1d('randomSeeds', [9001]*len(grid))
	return uniformSamplingLPEExperiment('uniformSamplingLPE20151116',
				[{'linearDrag':0.0, 'angularDrag':0.0}, {'linearDrag':0.2, 'angularDrag':0.2}],
				grid=grid,
				pointsPerJob=2,
				expectedWallClockTime='00:30:00')

if __name__ == '__main__':
	e = initializeExperiment()
	e.run()
