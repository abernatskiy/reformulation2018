#!/usr/bin/python2

from shared.grid import LogGrid,Grid1d
import tools.fileProcessors as tfp
import routes

from afpoForRunBasedLPE00 import initializeExperimentWithSeeds

def initializeExperiment():
	return initializeExperimentWithSeeds(28, 35, 'afpoForRunBasedLPE04')

if __name__ == '__main__':
	e = initializeExperiment()
	e.run()
