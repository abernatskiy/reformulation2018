from os.path import exists
import os

import pbsGridWalker.tools.algorithms as tal
import pbsGridWalker.tools.iniWriter as tiniw
import pbsGridWalker.tools.fsutils as tfs
import pbsGridWalker.tools.fileIO as tfio # for writeColumns()

import morphModRoutes as mmr
import classifiers

def prepareEnvironment(experiment):
	if not exists(mmr.arrowbotsExecutable):
		raise RuntimeError('Arrowbots executable not found at ' + mmr.arrowbotsExecutable)
	if not exists(mmr.evsExecutable):
		raise RuntimeError('EVS executable not found at ' + mmr.evsExecutable)

def runComputationAtPoint(worker, params, evsAdditionalParams, arrowbotsAdditionalParams, arrowbotInitialConditions, arrowbotTargetOrientations):
	print('Running evs-arrowbots pair with the following parameters: ' + str(params))
	parsedParams = tal.classifyDictWithRegexps(params, classifiers.serverClientClassifier)
	serverParams = tal.sumOfDicts(parsedParams['server'], evsAdditionalParams)
	print('Server params: ' + str(serverParams))
	clientParams = tal.sumOfDicts(parsedParams['client'], arrowbotsAdditionalParams)
	print('Client params: ' + str(clientParams))
	tiniw.write(serverParams, classifiers.evsClassifier, 'evs.ini')
	tiniw.write(clientParams, classifiers.arrowbotsClassifier, 'arrowbot.ini')
	tfio.writeColumns(arrowbotInitialConditions, 'initialConditions.dat')
	tfio.writeColumns(arrowbotTargetOrientations, 'targetOrientations.dat')

	geneFifo = tfs.makeUniqueFifo('.', 'genes')
	evalFifo = tfs.makeUniqueFifo('.', 'evals')

	clientProc = worker.spawnProcess([mmr.arrowbotsExecutable, geneFifo, evalFifo])
	if not worker.runCommand([mmr.evsExecutable, evalFifo, geneFifo, str(serverParams['randomSeed']), 'evs.ini']):
		return False
	worker.killProcess(clientProc, label='client')

	os.remove(geneFifo)
	os.remove(evalFifo)

	# TODO: Validation of the obtained files here

	return True
