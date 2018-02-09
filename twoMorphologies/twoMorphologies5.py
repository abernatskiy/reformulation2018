from os.path import join, exists, expanduser
from time import sleep
import subprocess
import sys
sys.path.append(join(expanduser('~'), 'morphMod'))

import pbsGridWalker.grid as gr
import pbsGridWalker.tools.algorithms as tal
import pbsGridWalker.tools.iniWriter as tiniw
import pbsGridWalker.tools.fsutils as tfs
import pbsGridWalker.tools.fileIO as tfio # for writeColumns()

import morphModRoutes as mmr
import classifiers

#dryRun = False

# Tunable hyperparameters
numTrials = 50
segments = 5
computationName = 'twoMorphologies_N' + str(segments)

# Constant hyperparameters
attachments = {'identity': 'J=I', 'null': 'J=0'}
initialPopulationTypes = ['sparse', 'random']
evsAdditionalParams = {'individual': 'trinaryWeights', 'communicator': 'unixPipe', 'evolver': 'cluneSimplified',
                       'length': 2*(segments**2), 'initLowerLimit': -1, 'initUpperLimit': 1, 'lowerCap': -1, 'upperCap': 1, 'mutExploration': 0.5, 'mutInsDelRatio': 1, 'mutationAmplitude': 1,
                       'populationSize': 50, 'genStopAfter': 500, 'secondObjectiveProbability': 1, 'logParetoFront': 'yes', 'logBestIndividual': 'yes', 'logParetoSize': 'yes',
                       'logParetoFrontKeepAllGenerations': 'yes', 'logParetoFrontPeriod': 1, 'backup': 'yes', 'trackAncestry': 'yes'}
arrowbotsAdditionalParams = {'segments': segments,
                             'simulationTime': 10., 'timeStep': 0.1, 'integrateError': 'no', 'writeTrajectories': 'no'}
arrowbotInitialConditions = [[0]*segments]*segments # segmentsXsegments null matrix
arrowbotTargetOrientations = [ [1 if i==j else 0 for i in range(segments)] for j in range(segments) ] # segmentsXsegments identity matrix

# Optional definitions for pbsGridWalker that depend on the number of segments
pointsPerJob = 10
maxJobs = 8
queue = 'shortq'
expectedWallClockTime = '03:00:00'

# Optional definitions for pbsGridWalker that are constant
involvedGitRepositories = mmr.involvedGitRepositories

# Required pbsGridWalker definitions
parametricGrid = gr.Grid1d('sensorAttachmentType', attachments.keys())*gr.Grid1d('initialPopulationType', initialPopulationTypes)*gr.Grid1dFromFile('randomSeed', mmr.randSeedFile, size=numTrials)

def prepareEnvironment(experiment):
	if not exists(mmr.arrowbotsExecutable):
		raise RuntimeError('Arrowbots executable not found at ' + mmr.arrowbotsExecutable)
	if not exists(mmr.evsExecutable):
		raise RuntimeError('EVS executable not found at ' + mmr.evsExecutable)

def runComputationAtPoint(worker, params):
	print('Running evs-arrowbots pair with the following parameters: ' + str(params))
	parsedParams = tal.classifyDict(params, classifiers.serverClientClassifier)
	serverParams = tal.sumOfDicts(parsedParams['server'], evsAdditionalParams)
	clientParams = tal.sumOfDicts(parsedParams['client'], arrowbotsAdditionalParams)
	tiniw.write(serverParams, classifiers.evsClassifier, 'evs.ini')
	tiniw.write(clientParams, classifiers.arrowbotsClassifier, 'arrowbot.ini')
	tfio.writeColumns(arrowbotInitialConditions, 'initialConditions.dat')
	tfio.writeColumns(arrowbotTargetOrientations, 'targetOrientations.dat')

	geneFifo = tfs.makeUniqueFifo('.', 'genes')
	evalFifo = tfs.makeUniqueFifo('.', 'evals')

	clientProc = worker.spawnProcess(['/users/a/b/abernats/arrowbots.olderr/arrowbotEvaluator', geneFifo, evalFifo])
	if not worker.runCommand([mmr.evsExecutable, evalFifo, geneFifo, str(serverParams['randomSeed']), 'evs.ini']):
		return False
	worker.killProcess(clientProc)
	# TODO: Validation of the obtained files here
	return True

def processResults(experiment):
	import os
	import shutil
	import numpy as np
	import pbsGridWalker.tools.plotutils as tplt
	tfs.makeDirCarefully('results', maxBackups=100)
	def fitnessFileName(sensAttType, initPopType):
		return 'SA' + sensAttType + '_IP' + initPopType + '_fitness'
	def columnExtractor(gp):
		outFile = fitnessFileName(gp['sensorAttachmentType'], gp['initialPopulationType'])
		subprocess.call('cut -d \' \' -f 2 bestIndividual*.log | tail -n +4 | tr \'\n\' \' \' >> ../results/' + outFile, shell=True)
		subprocess.call('echo >> ../results/' + outFile, shell=True)
	experiment.executeAtEveryGridPointDir(columnExtractor)
	os.chdir('results')
	xlabel = 'Generations'
	xlimit = 500
	ylimit = None
	xscale = 'log'
	yscale = 'log'
	margins = 0.5
	alpha=0.3
	def plotAllTSForInitalPopulationType(initPopType):
		title = None # 'Fitness time series for the two types of sensors attachment'
		dataDict = {attachments[x]: -1.*np.loadtxt(fitnessFileName(x, initPopType)) for x in attachments.keys()}
		tplt.plotAverageTimeSeries(dataDict, 'Error', 'errorComparison_GENS50_IP' + initPopType + '.png', title=title, legendLocation=None, xlabel=xlabel, xlimit=50, ylimit=ylimit, figsize=(2.5,4), xscale=xscale, yscale=yscale, margins=margins)
		tplt.plotAllTimeSeries(dataDict, 'Error', 'errorAllTrajectories_GEN50_IP' + initPopType + '.png', title=title, legendLocation=None, xlabel=xlabel, xlimit=50, ylimit=ylimit, figsize=(2.5,4), xscale=xscale, yscale=yscale, margins=margins, alpha=alpha)
		tplt.plotAverageTimeSeries(dataDict, 'Error', 'errorComparison_IP' + initPopType + '.png', title=title, legendLocation=1, xlabel=xlabel, xlimit=xlimit, ylimit=ylimit, xscale=xscale, yscale=yscale, margins=margins)
		tplt.plotAllTimeSeries(dataDict, 'Error', 'errorAllTrajectories_IP' + initPopType + '.png', title=title, legendLocation=3, xlabel=xlabel, xlimit=xlimit, ylimit=ylimit, xscale=xscale, yscale=yscale, margins=margins, alpha=alpha)
	for ip in initialPopulationTypes:
		plotAllTSForInitalPopulationType(ip)
	os.chdir('..')
