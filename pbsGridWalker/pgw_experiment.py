#!/usr/bin/env python2

import os
import sys
import shutil
import subprocess
import imp
from time import sleep

import routes
import gridSql
import tools.fsutils as tfs
import tools.algorithms as tal

sysEnv = imp.load_source('sysEnv', routes.sysEnv)
pbsEnv = imp.load_source('pbsEnv', routes.pbsEnv)

class Experiment(object):
	'''TODO: DESCRIPTION IS OUT OF DATE, REWRITE

     Abstract base class for Experiment classes, which are
	   supposed to help run computational experiments with
	   multiple parameters on PBS-based supercomputers.

	   User interface definitions (see helpstrings):
	     Experiment.__init__(self,
	       name,
	       experimentalConditions,
	       grid=None,
	       pointsPerJob=1,
	       queue=None,
	       expectedWallClockTime=None,
	       dryRun=False,
	       repeats=1
	     )
	     Experiment.run()

     Abstract methods:
       prepareEnv(self) - must create a suitable
         environment for the experiments.
         May include creating config files, compiling
         custom binaries, etc.
         Is executed at the work dir (./<name>).
       processResults(self) - processes the results.
         Is executed at the work dir (./<name>).

     Handy utilities for building processResults():
       executeAtEveryExperimentDir(self, function, cargs, kwargs)
       executeAtEveryConditionsDir(self, function, cargs, kwargs)
         - self-explanatory, works only within the work dir.
       enterWorkDir(self)
       exitWorkDir(self) - for user navigation when calling
         processResults() outside of run(),
         NOT NEEDED IN MOST CASES
	'''

	def __init__(self, descriptiveScript):
		'''Arguments:
       name: the name of the experiment and its
         working directory
       grid: describes the set of conditions under
         which we wish to see the computation's outcome.
         Must be iterable, indexable and yield parameter
         dictionaries with parameter names as keys and
         parameter values as values.
       pointsPerJob: indicates how many instances of
         computation should be performed within one
         cluster job. The default is one, meaning
         that each point of the parametric grid will be
         processed as a separate job. Useful for short
         jobs.
       passes: how many passes does your calculation
         require. Default is 1. Useful for very long
         computations with checkpointing.
       queue: the name of the queue which is to be used
         for the jobs. Default is specified on per-host
         basis in the defaultQueue variable at the host
         environment file (pointed to by pbsEnv variable
         at the routes.py).
       maxJobs: how many workers should the system spawn
         at any given moment. The default is
         ceil(len(grid)/pointPerJob), the maximum number of
         workers which can be ran concurrently without
         some of them waiting idle.
       expectedWallClockTime: a scheduler-parsable string
         desribing a time span of a single job. Examples:
           03:00:00 - three hours
           7:00:00:00 - seven days
         Cutoff time of the queue is used by default.
       repos: Experiment class automatically checks and
         stores info about versions and diffs of git
         repositories used in the computation. By default
         it will only monitor its own version; add all the
         other software it uses here. The format is:
           {'componentName': 'pathToComponentsRepo'}
         You will probably want to fix this variable in
         daughter classes.
			 dryRun: set to true to perform a dry run.
		'''
		self.descriptiveScript = os.path.abspath(descriptiveScript)
		self.description = imp.load_source('desc', self.descriptiveScript)

		# Checking the descriptive script for required attributes
		requiredDescriptiveScriptAttributes = ['computationName', 'parametricGrid', 'prepareEnvironment', 'processResults', 'runComputationAtPoint']
		for reqAttr in requiredDescriptiveScriptAttributes:
			if not hasattr(self.description, reqAttr):
				raise ValueError('Description script lacks a required attribute ' + reqAttr)

		self.name = self.description.computationName
		self._checkFSNameUniqueness(self.description.parametricGrid)
		self.grid = self.description.parametricGrid

		# Treating optional attributes of the description
		self._assignOptionalHyperparameter('pointsPerJob', 1)
		self._assignOptionalHyperparameter('passes', 1)
		if self.passes > 1 and self.pointsPerJob > 1:
			print('WARNING: You\'re trying to run a multistage job with more than one grid point per job. It is advisable to split computation into grid points as much as possible before splitting the points themselves')
		self._assignOptionalHyperparameter('queue', pbsEnv.defaultQueue)
		self.totalJobs = tal.ratioCeil(len(self.grid), self.pointsPerJob)
		if hasattr(self.description, 'maxJobs'):
			self.maxJobs = min(self.totalJobs, self.description.maxJobs)
		else:
			self.maxJobs = self.totalJobs
		self._assignOptionalHyperparameter('expectedWallClockTime', pbsEnv.queueLims[self.queue])
		self._assignOptionalHyperparameter('involvedGitRepositories', {})
		self._assignOptionalHyperparameter('maxFailures', 10)
		self._curJobIDs = []
		self.dbname = 'experiment.db'

	def _assignOptionalHyperparameter(self, paramName, defaultValue):
		setattr(self, paramName, defaultValue if not hasattr(self.description, paramName) else getattr(self.description, paramName))

	# Convenience functions - use these in definitions of the abstract methods

	def makeNote(self, line):
		with open('experimentNotes.txt', 'a') as noteFile:
			noteFile.write(line + '\n')

	# Core methods

	def prepareEnvironment(self):
		tfs.makeDirCarefully(self.name)
		self.enterWorkDir()
		self.makeNote('Experiment ' + self.name + ' initiated at ' + self._dateTime())
		self._recordVersions()
		self.makeNote('Apps versions recorded successfully')
		gridSql.makeGridTable(self.grid, self.dbname)
		gridSql.makeGridQueueTable(self.dbname, passes=self.passes)
		self.description.prepareEnvironment(self)
		self.exitWorkDir()

	def run(self):
		self.enterWorkDir()
		# farm workers
		jobsSubmitted = 0 # or attempted
		jobsExpected = self.totalJobs*self.passes
		while not gridSql.checkForCompletion(self.dbname):
			self._weedWorkers()
			while not gridSql.checkForUntreatedPoints(self.dbname) and len(self._curJobIDs) < self.maxJobs:
				self._spawnWorker()
				jobsSubmitted += 1
				sys.stdout.write('\rsubmitted job {}/{}'.format(jobsSubmitted, jobsExpected))
				sys.stdout.flush()
				sleep(pbsEnv.qsubDelay)
				if jobsSubmitted > jobsExpected:
					self.makeNote('Expected {} jobs, submitted {}: likely some workers failed'.format(jobsExpected, jobsSubmitted))
					if jobsSubmitted-jobsExpected >= 10:
						self.makeNote('10 jobs submitted in addition to what was expected. Will not clog the queue any further. Exiting.')
						sys.exit(1)
			nf = gridSql.numFailures(self.dbname)
			if gridSql.numFailures(self.dbname)>self.maxFailures:
				self.makeNote('Too many falures (>{}), exiting'.format(self.maxFailures))
				sys.exit(1)
			sleep(pbsEnv.qstatCheckingPeriod)
		print('\nDone')
		self.exitWorkDir()

	def processResults(self):
		self.enterWorkDir()
		self.description.processResults(self)
		self.exitWorkDir()

	# Internals

	def enterWorkDir(self):
		if not os.path.isdir(self.name):
			raise OSError('Cannot find working dir ' + self.name)
		os.chdir(self.name)

	def exitWorkDir(self):
		os.chdir('..')

	def _checkFSNameUniqueness(self, iterable):
		dirNames = map(tfs.dictionary2filesystemName, iterable)
		if not len(dirNames) == len(set(dirNames)):
			raise ValueError('Dirnames produces by the grid are not all unique:\n' + '\n'.join(dirNames))

	def _dateTime(self):
		return subprocess.check_output([sysEnv.date])[:-1]

	def _recordVersions(self):
		def pathVerRecord(file, repoName, repoPath):
			curDir = os.getcwd()
			os.chdir(repoPath)
			versionStr = subprocess.check_output([sysEnv.git, 'rev-parse', 'HEAD'])
			branchOut = subprocess.check_output([sysEnv.git, 'branch'])
			branchStr = filter(lambda str: str.find('* ') == 0, branchOut.split('\n'))[0].replace('* ', '')
			diffStr = subprocess.check_output([sysEnv.git, 'diff'])
			file.write(repoName + ' path: ' + repoPath + '\n' +
									repoName + ' branch: ' + branchStr + '\n' +
									repoName + ' version: ' + versionStr + '\n' +
									'git diff for ' + repoName + ':\n' + diffStr +'\n' +
									'-------------------------\n')
			os.chdir(curDir)
		with open('versions.txt', 'w') as verFile:
			pathVerRecord(verFile, 'pbsGridWalker', routes.pbsGridWalker)
			for repoName, repoPath in self.involvedGitRepositories.items():
				pathVerRecord(verFile, repoName, repoPath)
			verFile.write('\nDescriptive script listing:\n\n')
			with open(self.descriptiveScript, 'r') as dsFile:
				shutil.copyfileobj(dsFile, verFile, 10240)

	def _spawnWorker(self):
		cmdList = [pbsEnv.qsub,
			'-q', self.queue,
			'-l',  'walltime=' + self.expectedWallClockTime,
			'-v', 'PYTHON=' + sys.executable +
						',PBSGRIDWALKER_HOME=' + routes.pbsGridWalker +
						',PARENT_SCRIPT=' + self.descriptiveScript +
						',POINTS_PER_JOB=' + str(self.pointsPerJob),
			os.path.join(routes.pbsGridWalker, 'pbs.sh')]
		commandLine = subprocess.list2cmdline(cmdList)
		self.makeNote('qsub command: ' + commandLine)
		for t in range(60):
			try:
				curJobID = subprocess.check_output(cmdList)
				break
			except:
				self.makeNote('Command ' + commandLine + ' failed on attempt {} of {}, retrying in 10 seconds'.format(t, 60))
				sleep(10)
		schedulerCheckingPeriod = 0.2 # seconds
		for t in xrange(int(pbsEnv.waitForTheScheduler/schedulerCheckingPeriod)):
			if curJobID in subprocess.check_output([pbsEnv.qstat, '-f', '-u', pbsEnv.user]):
				self.makeNote('Job ' + curJobID + ' was successfully submitted')
				#print('Job ' + curJobID + ' was successfully submitted')
				self._curJobIDs.append(curJobID)
				return True
			sleep(schedulerCheckingPeriod)
		self.makeNote('Failed to submit job: qsub worked, but the job did not apper in queue within {} seconds'.format(pbsEnv.waitForTheScheduler))
		return False

	def _weedWorkers(self):
		cmdList = [pbsEnv.qstat, '-f', '-u', pbsEnv.user]
		qstat = subprocess.check_output(cmdList)
		self._curJobIDs = [ jobID for jobID in self._curJobIDs if jobID in qstat ]

	def executeAtEveryGridPointDir(self, function, *cargs, **kwargs):
		'''The function must accept a grid point parameter dictionary as its first argument'''
		for gridPoint in self.grid:
			gpDirName = tfs.dictionary2filesystemName(gridPoint)
			try:
				os.chdir(gpDirName)
				args = (gridPoint,) + cargs
				function(*args, **kwargs)
				os.chdir('..')
			except OSError as err:
				print('\033[93mWarning!\033[0m Could not enter directory \033[1m' + err.filename + '\033[0m')

if __name__ == '__main__':
	import argparse
	cliParser = argparse.ArgumentParser(description='Run all the computations for a given description script')
	cliParser.add_argument('scriptPath', metavar='path_to_script', type=str, help='path to the description script')
	cliArgs = cliParser.parse_args()
	e = Experiment(cliArgs.scriptPath)
	e.prepareEnvironment()
	e.run()
	e.processResults()
