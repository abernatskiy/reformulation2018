import os
import subprocess
import imp
from copy import copy
from abc import abstractmethod

import routes
import shared.grid
import shared.translators
from experiment import Experiment

sysEnv = imp.load_source('sysEnv', routes.sysEnv)
pbsEnv = imp.load_source('pbsEnv', routes.pbsEnv)

def _dictionary2CeGccOptions(dict):
	numericalParams = {	'angularGain': 'ANGULAR_GAIN',
											'forceGain': 'FORCE_GAIN',
											'sensorGain': 'SENSOR_GAIN',
											'robotRadius': 'ROBOT_RADIUS',
											'robotHeight': 'RHEIGHT',
											'linearDrag': 'LINEAR_DRAG_COEFFICIENT',
											'angularDrag': 'ANGULAR_DRAG_COEFFICIENT',
											'tailScale': 'TAIL_SCALE' }
	booleanParams = {	'firstOrderDynamics': 'FIRST_ORDER_DYNAMICS',
										'withOcclusion': 'WITH_OCCLUSION',
										'withGraphics': 'WITH_GRAPHICS',
										'withScreenshots': 'WITH_SCREENSHOTS' }
	def paramString(paramName, dict):
		if paramName in numericalParams:
			return '-D' + numericalParams[paramName] + '=' + str(dict[paramName])
		elif paramName in booleanParams:
			return '-D' + booleanParams[paramName] if dict[paramName] != 0.0 else ''
		else:
			return ''
	return ' '.join([ paramString(paramName, dict) for paramName in dict.keys() ])

class staticEvsDynamicCeExperiment(Experiment):
	'''Abstract base class for Expertiments which use
     the same EVS config, but different cylindersEvasion
     binaries for every run.

     Abstract methods:
       processResult(self) - processes the results.
         Inherited from Experiment.
       evsConfig(self) - returns the EVS config as a
         string.
	'''

	def prepareEnv(self):
		super(staticEvsDynamicCeExperiment, self).prepareEnv()
		self._writeEvsConfig()
		self._prepareClientBinaries()

	def _writeEvsConfig(self):
		f = open('config.ini', 'w')
		f.write(self.evsConfig())
		f.close()

	@abstractmethod
	def evsConfig(self):
		pass

	def _prepareClientBinaries(self):
		mainExpDir = os.getcwd()
		os.makedirs('bin')
		os.chdir(routes.clientHome)
		for gridParams in self.grid:
			for experimentalParams in self.experimentalConditions:
				fullParams = copy(gridParams)
				fullParams.update(experimentalParams)
				clientBinaryPath = os.path.join(mainExpDir, 'bin', 'cylindersEvasion_' + shared.translators.dictionary2FilesystemName(fullParams))
				if not self.dryRun:
					self._compileClient(fullParams, clientBinaryPath)
				else:
					clientBinaryDummy = open(clientBinaryPath, 'w')
					clientBinaryDummy.close()
		os.chdir(mainExpDir)

	def _compileClient(self, params, outPath):
		'''Must operate at routes.clientHome directory'''
		optionsStr = _dictionary2CeGccOptions(params)

		FNULL = open(os.devnull, 'w')
		logFile = open(outPath + '.makestderr', 'w')

		subprocess.check_call([sysEnv.make, 'clean'], stdout=FNULL)
		subprocess.check_call(sysEnv.make + ' -j' + str(pbsEnv.maxRootNodeThreads) + ' MORECFLAGS="' + optionsStr + '"' , shell=True, stdout=FNULL, stderr=logFile)

		logFile.close()
		FNULL.close()

		os.rename('cylindersEvasion', outPath)
