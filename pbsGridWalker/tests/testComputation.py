from os.path import join
from time import sleep

import grid
import routes

sleepyTime = 5

# required definitions
computationName = 'testComputation'
parametricGrid = grid.Grid1d('someTruth', [0, 1])
def prepareEnvironment(experiment):
	print('Sleepy time~')
	sleep(sleepyTime)
	with open('preparations.txt', 'w') as f:
		f.write('Preparations done!\n')
def processResults(experiment):
	print('Sleepy time~')
	sleep(sleepyTime)
	with open('results.txt', 'w') as f:
		f.write('Results processed!\n')
def runComputationAtPoint(worker, params):
	print('Sleepy time~')
	sleep(sleepyTime)
	with open('logs.txt', 'w') as f:
		f.write('Computation with params ' + str(params) + ' completed successfully!\n')
	return True

# auxiliary definitions
#pointsPerJob = 1
#passes = 1
queue = 'shortq'
#maxJobs = 1
expectedWallClockTime = '00:05:00'
#involvedGitRepositories = {'evs': join(routes.home, 'evs')}
#dryRun = False
#maxFailures = 10
