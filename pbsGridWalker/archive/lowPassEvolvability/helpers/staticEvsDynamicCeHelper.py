#!/usr/bin/python2

import subprocess
import imp
import os
import sys
from time import sleep

from helper import Helper

class staticEvsDynamicCeHelper(Helper):
	def __init__(self, argv):
		super(staticEvsDynamicCeHelper, self).__init__(argv)
		self.sysEnv = imp.load_source('sysEnv', self.routes.sysEnv)

	def runGroup(self, fcond):
		self._makeFIFOs()
		self._spawnClient(fcond)
		for seed in self._listSeeds(fcond):
			self._runServer(fcond, seed)
		self._killClient()
		self._ensureProcessesEnd()
		self._removeFIFOs()
		self._preprocessResults(fcond)

	def _listSeeds(self, fcond):
		outSeeds = []
		if fcond.has_key('randomSeeds'):
			seeds = fcond['randomSeeds']
			if type(seeds) == int:
				return [seeds]
			elif type(seeds) == list and all([type(seed) == int for seed in seeds]):
				return seeds
			else:
				raise ValueError('Wrong specification of randomSeeds, must be an integer or a list of integers (got ' + type(seeds) + ')')
		else:
			raise ValueError('randomSeeds not specified in conditions. Add it and make it either an integer or a list of integers')

	def _makeFIFOs(self):
		subprocess.call([self.sysEnv.mkfifo, 'genes'])
		subprocess.call([self.sysEnv.mkfifo, 'evals'])
		curDir = os.getcwd()
		self.genesPipe = os.path.join(curDir, 'genes')
		self.evalsPipe = os.path.join(curDir, 'evals')

	def _spawnClient(self, fcond):
		clientBinary = os.path.join(self.rootDir, 'bin', 'cylindersEvasion_' + self.translators.dictionary2FilesystemName(fcond))
		cmdList = [clientBinary, self.genesPipe, self.evalsPipe]
		self._makeGroupNote('Starting the client: ' + subprocess.list2cmdline(cmdList) + ' (at ' + os.getcwd() + ')')
		self.clientProc = subprocess.Popen(cmdList)

	def _runServer(self, fcond, randSeed):
		if self.repeat == 0:
			configPath = self._getEvsConfig(fcond)
			cmdList = [sys.executable, self.routes.evsExecutable, self.evalsPipe, self.genesPipe, str(randSeed), configPath]
		else:
			cmdList = [sys.executable, self.routes.evsResume]
		self._makeGroupNote('Executing the server: ' + subprocess.list2cmdline(cmdList) + ' (at ' + os.getcwd() + ')')
		subprocess.check_call(cmdList)

	def _getEvsConfig(self, fcond):
		return os.path.join(self.rootDir, 'config.ini')

	def _killClient(self):
		self._makeGroupNote('Killing the client...')
		self.clientProc.send_signal(subprocess.signal.SIGTERM)

	def _ensureProcessesEnd(self):
		sleep(1) # TODO: better implementation

	def _removeFIFOs(self):
		subprocess.call([self.sysEnv.rm, self.genesPipe])
		subprocess.call([self.sysEnv.rm, self.evalsPipe])

	def _preprocessResults(self, conditions):
		pass

if __name__ == '__main__':
	f = open('helpernotes' + sys.argv[2] + '.txt', 'w')
	f.write('Arguments: ' + str(sys.argv) + '\n')
	f.write('Attempting to create Helper...\n')
	f.flush()
	h = staticEvsDynamicCeHelper(sys.argv)
	f.write(str(h))
	f.close()
	h.runExperiments()
	print('DONE')
