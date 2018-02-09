#!/usr/bin/python2

import sys
import os
from time import sleep,time
from copy import copy
import imp
import subprocess

import routes
import gridSql
import tools.fsutils as tfs

def _getTimeString(tsecs):
	m, s = divmod(tsecs, 60)
	h, m = divmod(m, 60)
	return '%d:%02d:%02d' % (h, m, s)

class Worker(object):
	'''Abstract base class for Worker objects which handle the execution
     of the experiment processes at cluster nodes.

     Will use the function runComputationAtPoint(worker, fullConditions)
	   from the parent script to execute the computation at exactly one
	   point in parametric space. The function can assume that it will be
	   executed from within the point's directory. It must return True iff
	   the computation was completed successfully.
	'''
	def __init__(self, argv):
		'''Should be constructed from sys.argv
       Fields:
         argv[0] - worker script name, ignored
         argv[1] - parent script
		     argv[2] - number of points the worker should attempt to process
		       within its life cycle
		'''
		self.pbsGridWalker = routes.pbsGridWalker
		self.parentScript = imp.load_source('parent', argv[1])
		self.runComputationAtPoint = self.parentScript.runComputationAtPoint
		self.pointsPerJob = int(argv[2])
		self.rootDir = os.getcwd()
		self.dbname = os.path.abspath('experiment.db')
		self.dryRun = False if not hasattr(self.parentScript, 'dryRun') else self.parentScript.dryRun

	def __repr__(self):
		return( 'Worker: pbsGridWalker = ' + str(self.pbsGridWalker) + '\n' +
						'        parentScript = ' + str(self.parentScript) + '\n' +
						'        rootDir = ' + self.rootDir + '\n' +
						'        pointsPerJob = ' + str(self.pointsPerJob) + '\n')

	def __str__(self):
		return repr(self)

	def spawnProcess(self, cmdList):
		if not self.dryRun:
			self.makeGroupNote('Spawning a process with command ' + subprocess.list2cmdline(cmdList) + ' at ' + os.getcwd())
			return subprocess.Popen(cmdList)
		else:
			self.makeGroupNote('Doing a dry run. Would spawn a process with command ' + subprocess.list2cmdline(cmdList) + ' at ' + os.getcwd())
			return None

	def killProcess(self, process, label='unknown'):
		if not self.dryRun:
			self.makeGroupNote('Killing a process (pid {}, label {})'.format(process.pid, label))
			process.send_signal(subprocess.signal.SIGTERM)
		else:
			self.makeGroupNote('Doing a dry run. Would kill a process')

	def runCommand(self, cmdList):
		command = subprocess.list2cmdline(cmdList)
		if not self.dryRun:
			self.makeGroupNote('Running command ' + command + ' at ' + os.getcwd())
			try:
				subprocess.check_call(cmdList)
				return True
			except subprocess.CalledProcessError:
				self.makeGroupNote('Command ' + command + ' failed')
				return False
		else:
			self.makeGroupNote('Doing a dry run. Would run command ' + command + ' at ' + os.getcwd())
			return True

	def makeGroupNote(self, str):
		print(str)
		with open('groupNotes.txt', 'a') as f:
			f.write(str + '\n')

	def runAtAllPoints(self):
		maxPoints = self.pointsPerJob
		while self.pointsPerJob > 0:
			pointTriple = gridSql.requestPointFromGridQueue(self.dbname)
			if pointTriple:
				id, curPass, params = pointTriple
				gpDirName = tfs.dictionary2filesystemName(params)
				tfs.makeDirCarefully(gpDirName)
				os.chdir(gpDirName)

				self.makeGroupNote('Processing grid point {}'.format(id))
				self.makeGroupNote('Grid parameters of the run conducted here: ' + str(params))
				elapsedTime = time()
				if self.runComputationAtPoint(self, params):
					self.makeGroupNote('Computation at grid point {} completed successfully'.format(id))
					gridSql.reportSuccessOnPoint(self.dbname, id)
				else:
					self.makeGroupNote('Computation at grid point {} failed'.format(id))
					gridSql.reportFailureOnPoint(self.dbname, id)
				elapsedTime = time() - elapsedTime
				self.makeGroupNote('Run completed in ' + str(elapsedTime) + ' seconds (' + _getTimeString(elapsedTime) + ' hours) of wall clock time')

				os.chdir('..')

				self.pointsPerJob -= 1
			else:
				print('WORKER: No points left in the grid, finishing walking the grid before the allowed number of points per job ({}) has been reached.'.format(maxPoints))
				print('WORKER: Exiting after completing the computation at {} points of the grid.'.format(maxPoints - self.pointsPerJob))
				return
		print('WORKER: Hit the allowed number of points per job ({}), finishing walking the grid.'.format(maxPoints))

if __name__ == '__main__':
	workerTime = time()
	w = Worker(sys.argv)
	w.runAtAllPoints()
	workerTime = time() - workerTime
	print('WORKER: Finished in ' + str(workerTime) + ' seconds')
