#!/usr/bin/python2

import os
import numpy as np
import subprocess

import staticEvsDynamicCeExperiment as sedce
from shared.grid import LogGrid,Grid1d

import tools.fileProcessors as tfp
import routes

def mkdir(dirname):
	if not os.path.isdir(dirname):
		os.makedirs(dirname)

class afpoForRunBasedLPEExperiment(sedce.staticEvsDynamicCeExperiment):
	def processResults(self):
#		for updir in ./*; do cd $updir; for dir in ./*; do if [ -d $dir ]; then cd ${dir}; mkdir tmp; for file in bestIndividual*.log; do cat $file | grep -v \# | cut -d ' ' -f2 > tmp/$file; done; paste -d ' ' tmp/* > ../${dir}.fitness; rm -r tmp; cd ..; fi; done; cd ..; done

#		def testFunc(gridPoint, condPoint, self, testStr, fgs=''):
#			print('Args: ' + str(gridPoint))
#		self.executeAtEveryConditionsDir(testFunc, (self, 'testarg'), {'fgs': 'fds'})
		import shutil
		from shared.translators import dictionary2FilesystemName
#		globalResultsDir = os.path.join(routes.home, 'afpoForLPEResults')
		globalResultsDir = os.path.join('/slowstorage/lpeArchives', 'afpoForLPEResults')
		mkdir(globalResultsDir)
		def grabAllTS(gridPoint, condPoint, self, globalResultsDir):
			gains = {x: gridPoint[x] for x in ['sensorGain', 'forceGain']}
			drags = {x: gridPoint[x] for x in ['linearDrag', 'angularDrag']}
			gainsDir = os.path.join(globalResultsDir, dictionary2FilesystemName(gains))
			dragsDir = os.path.join(gainsDir, dictionary2FilesystemName(drags))
			mkdir(gainsDir)
			mkdir(dragsDir)
			filename = 'bestIndividual' + str(gridPoint['randomSeeds']) + '.log'
			shutil.copyfile(filename, os.path.join(dragsDir, filename))
		self.executeAtEveryConditionsDir(grabAllTS, (self, globalResultsDir), {})

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
						'backupPeriod = 1000\n'
						'genStopAfter = 50000\n')

def afpoBaseGrid():
	sgGrid = LogGrid('sensorGain', 1, 16, 0, 1)
	fgGrid = LogGrid('forceGain', 0.8, 16, 1, 1)
	expCondGrid = Grid1d('linearDrag', [0.0, 0.2]) + Grid1d('angularDrag', [0.0, 0.2])
	return sgGrid*fgGrid*expCondGrid

def initializeExperimentWithSeeds(beginSeed, endSeed, expName):
	grid = afpoBaseGrid()
	randSeedsList = tfp.randSeedList(os.path.join(routes.evscriptsHome, 'seedFiles', 'randints1416551751.dat'), size=200)
	grid *= Grid1d('randomSeeds', randSeedsList[beginSeed:endSeed])
	return afpoForRunBasedLPEExperiment(expName,
					[{}],
					grid=grid,
					expectedWallClockTime='29:00:00',
					queue='workq',
					repeats=4)

def initializeExperiment():
	return initializeExperimentWithSeeds(0, 7, 'afpoForRunBasedLPE00')

if __name__ == '__main__':
	e = initializeExperiment()
	e.run()
