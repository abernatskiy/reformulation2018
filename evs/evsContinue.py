#!/usr/bin/python2

import sys
import os
import cPickle

def loadLastPickle():
	bcfolder = 'backups'
	if not os.path.isdir(bcfolder):
		raise OSError(bcfolder + ' directory not found, cannot continue')
	files = os.listdir(bcfolder)
	files = filter(lambda x: x.endswith('.p'), files)
	files.sort()
	files.reverse()
	evolver = None
	for curFileName in files:
		fullFileName = os.path.join('backups', curFileName)
		with open(fullFileName, 'r') as curFile:
			try:
				print 'Trying to load ' + fullFileName + ' ...',
				evolver = cPickle.load(curFile)
				print 'success!'
				break
			except:
				print 'failure'
				continue
	if evolver is None:
		raise OSError('Could not find any suitable pickles at ' + bcfolder + ', cannot continue')
	else:
		return evolver

if len(sys.argv) == 1:
	evolver = loadLastPickle()
elif len(sys.argv) == 2:
	with open(sys.argv[1], 'r') as file:
		evolver = cPickle.load(file)
else:
	print('Usage: evsContinue.py [<backupPickleFileName>]\n'
				'If no backup file is given, the program automatically searches for the one with a highest number at backups/')
	sys.exit(1)

evolver.recover()
evolver.generateLogsAndStdout()

while True:
	evolver.updatePopulation()
	evolver.pickleSelf()
	evolver.generateLogsAndStdout()

