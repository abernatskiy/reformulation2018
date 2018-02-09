#!/usr/bin/python2

import os
import numpy as np
import subprocess

import staticEvsDynamicCeExperiment as sedce
from shared.grid import LogGrid,Grid1d

import tools.fileProcessors as tfp
import routes

class afpoForRunBasedLPEExperiment(sedce.staticEvsDynamicCeExperiment):
	def processResults(self):
		pass

	def evsConfig(self):
		return ('[classes]\n'
						'individual = trinaryVectorSureMutation\n'
						'communicator = chunkedUnixPipe\n'
						'evolver = afpo\n'
						'\n'
						'[indivParams]\n'
						'length = 60\n'
						'\n'
						'[evolParams]\n'
						'populationSize = 400\n'
						'logBestIndividual = yes\n'
						'backup = yes\n'
						'backupPeriod = 1\n'
						'genStopAfter = 50000\n')

def afpoBaseGrid():
	sgGrid = LogGrid('sensorGain', 1, 16, 0, 1)
	fgGrid = LogGrid('forceGain', 0.8, 16, 1, 1)
	expCondGrid = Grid1d('linearDrag', [0.0, 0.2]) + Grid1d('angularDrag', [0.0, 0.2])
	return sgGrid*fgGrid*expCondGrid

def initializeExperiment():
	grid = afpoBaseGrid()
	randSeedsList = tfp.randSeedList(os.path.join(routes.evscriptsHome, 'seedFiles', 'randints1416551751.dat'), size=200)
#	grid *= Grid1d('randomSeeds', randSeedsList[0:7])
	grid *= Grid1d('randomSeeds', randSeedsList[0:1])
	return afpoForRunBasedLPEExperiment('afpoForRunBasedLPE20151222',
					[{}],
					grid=grid,
#					expectedWallClockTime='29:00:00',
					expectedWallClockTime='00:05:00',
#					queue='workq',
					queue='shortq',
					repeats=3)

if __name__ == '__main__':
	e = initializeExperiment()
	e.run()
