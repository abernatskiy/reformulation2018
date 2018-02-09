from copy import deepcopy
import numpy as np
import os

import sys
sys.path.append('..')
from commons import afpr, translateParametersDictionary, emptyParametersTranslator

def firstDominatedBySecondManyObjectives(first, second, functions, breakTiesByIDs=True):
	'''Assumes all functions are minimized'''
	if first.id == second.id:
		raise RuntimeError('Pareto optimization error: Two individuals with the same ID compared:\n' + str(first) + '\n' + str(second))
	vals = [ (func(first), func(second)) for func in functions ]
	if all([ f >= s for f,s in vals ]) and any([ f > s for f,s in vals ]):
		return True
	elif breakTiesByIDs and all([ f == s for f,s in vals ]):
		return first.id < second.id
	else:
		return False

def firstDominatedBySecond(indiv0, indiv1, func0, func1, breakTiesByIDs=True):
	'''Assumes that both functions are minimized, as in the classical Pareto front picture'''
	# truth table:
	#                  f0(i0)<f0(i1)    f0(i0)=f0(i1)    f0(i0)>f0(i1)
	# f1(i0)<f1(i1)    F                F                F
	# f1(i0)=f1(i1)    F                ID0<ID1          T
	# f1(i0)>f1(i1)    F                T                T
	if indiv0.id == indiv1.id:
		raise RuntimeError('Pareto optimization error: Two individuals with the same ID compared:\n' + str(indiv0) + '\n' + str(indiv1))
	if func0(indiv0) == func0(indiv1):
		if func1(indiv0) == func1(indiv1):
			if breakTiesByIDs:
				return indiv0.id < indiv1.id # lower ID indicates that indiv0 was generated before indiv1 and is older
			else:
				return False
		else:
			return func1(indiv0) > func1(indiv1)
	else:
		return func0(indiv0) > func0(indiv1) and func1(indiv0) >= func1(indiv1)

def firstStochasticallyDominatedBySecond(indiv0, indiv1, func0, func1, secondObjProb):
	if np.random.random() > secondObjProb:
		if func0(indiv0) > func0(indiv1):
			#print('{} was beaten by {} with pure fitness'.format(indiv0, indiv1))
			return True
		elif func0(indiv0) == func0(indiv1):
			return indiv0.id < indiv1.id # lower ID indicates that indiv0 was generated before indiv1 and is older
		else:
			return False
	else:
		if firstDominatedBySecond(indiv0, indiv1, func0, func1):
			#print('{} was beaten by {} with with two objectives'.format(indiv0, indiv1))
			return True
		else:
			return False

class BaseEvolver(object):
	'''Base class for evolutionary algorithms. Provides
     methods for creating server output.'''
	def __init__(self, communicator, indivParams, evolParams, initialPopulationFileName = None):
		self.params = translateParametersDictionary(evolParams, self.optionalParametersTranslator(), requiredParametersTranslator=self.requiredParametersTranslator())
		self.communicator = communicator
		self.indivParams = indivParams
		self.logHeaderWritten = False
		self.generation = 0
		if self.params.has_key('randomSeed'):
			np.random.seed(self.params['randomSeed'])
		if self.paramIsEnabled('trackAncestry'):
			indivParams['trackAncestry'] = True

		self._createGlobalGenerationCounter()
		self._setGlobalGenerationCounter()

		self.population = []
		if not initialPopulationFileName is None:
			self._appendPopulationFromFile(initialPopulationFileName)

	def optionalParametersTranslator(self):
		t = emptyParametersTranslator()
		t['toBool'].add('logParetoFrontKeepAllGenerations')
		t['toInt'].update({'genStopAfter',
		                    'populationSize',
		                    'randomSeed'})
		periodicActionBools = {'logPopulation',
		                       'logBestIndividual',
		                       'printBestIndividual',
		                       'printParetoFront',
		                       'printPopulation',
		                       'backup',
		                       'printGeneration',
		                       'logParetoFront'}
		t['toBool'].update(periodicActionBools)
		t['toInt'].update({ x + 'Period' for x in periodicActionBools })
		t['toFloat'].update({'noiseAmplitude', 'secondObjectiveProbability'})
		return t

	def requiredParametersTranslator(self):
		return emptyParametersTranslator()

	def updatePopulation(self):
		self.generation += 1
		self._setGlobalGenerationCounter()
		if self.params.has_key('genStopAfter') and self.generation > self.params['genStopAfter']:
			self.done()

	def done(self):
		print 'Done.\n'
		import sys
		sys.exit(0)

	def pickleSelf(self, postfix=''):
		if not self._shouldIRunAPeriodicFunctionNow('backup'):
			return
		self.randomGeneratorState = np.random.get_state()
		if not hasattr(self, '__pickleSelfCalled__'):
			self.__pickleSelfCalled__ = True
			import os
			import time
			import shutil
			if os.path.isdir('./backups'):
				print 'Old phenotypes found. Moving to a backups.save folder'
				if os.path.exists('./backups.save'):
					print 'WARNING! Phenotype save folder found at backups.save. Overwriting in 10 seconds, press Ctrl+C to abort...'
					time.sleep(10)
					shutil.rmtree('./backups.save')
					print 'Folder backups.save erased'
				shutil.move('./backups', './backups.save')
				os.mkdir('./backups')
			elif os.path.exists('./backups'):
				raise IOError('Backups path exists, but is not a directory')
			else:
				os.mkdir('./backups')
		if not hasattr(self, '__pickleLoaded__') or not self.__pickleLoaded__:
			global cPickle
			import cPickle
			self.__pickleLoaded__ = True
		with open('./backups/' + str(self.generation).zfill(10) + postfix + '.p', 'w') as file:
			self.__pickleLoaded__ = False
			cPickle.dump(self, file)
			self.__pickleLoaded = True

	def recover(self):
		map(lambda x: x.recoverID(), self.population)   # make sure that we start from the next free ID
		np.random.set_state(self.randomGeneratorState)
		self._createGlobalGenerationCounter()
		self._setGlobalGenerationCounter()
		if self.paramIsEnabled('logBestIndividual'):
			self._truncateLogFile(self._bestIndividualLogFileName)
		if self.paramIsEnabled('logConcatenatedPopulation'):
			self._truncatePopulationFile('population0.log')

	def _truncatePopulationFile(self, filename):
		smallestID = 50000000
		for indiv in self.population:
			smallestID = indiv.id if indiv.id < smallestID else smallestID
		print 'Splitting at ' + str(largestID)
		oldFilename = filename + '.old'
		os.rename(filename, oldFilename)
		with open(oldFilename, 'r') as oldFile:
			with open(filename, 'w') as file:
				for s in oldFile:
					if s.split(' ')[1] == str(largestID):
						break
					file.write(s)
		os.remove(oldFilename)

	def _truncateLogFile(self, filename):
		oldFilename = filename + '.old'
		os.rename(filename, oldFilename)
		with open(oldFilename, 'r') as oldFile:
			with open(filename, 'w') as file:
				for s in oldFile:
					if s.startswith(str(self.generation)):
						break
					file.write(s)
		os.remove(oldFilename)

	def _printGeneration(self):
		if not self._shouldIRunAPeriodicFunctionNow('printGeneration'):
			return
		print 'Generation ' + str(self.generation)

	def _printBestIndividual(self):
		if not self._shouldIRunAPeriodicFunctionNow('printBestIndividual'):
			return
		bestIndiv = self.population[-1]
		print 'Best individual: ' + str(bestIndiv) + ' score: ' + str(bestIndiv.score)

	def _printPopulation(self):
		if not self._shouldIRunAPeriodicFunctionNow('printPopulation'):
			return
		print '-----------'
		for indiv in self.population:
			print str(indiv) + ' score: ' + str(indiv.score)
		print ''

	def printParetoFront(self, paretoFront, objname, objfunc):
		if not self._shouldIRunAPeriodicFunctionNow('printParetoFront'):
			return
		print 'Pareto front:'
		for indiv in paretoFront:
			print str(indiv) + ' score: ' + afpr(indiv.score) + ' ' + objname + ': ' + str(objfunc(indiv))
		print ''

	def printParetoFrontMultipleObjectives(self, paretoFront, functions, labels):
		if not self._shouldIRunAPeriodicFunctionNow('printParetoFront'):
			return
		print 'Pareto front:'
		for indiv in paretoFront:
			outstr = str(indiv)
			for f, l in zip(functions, labels):
				outstr += ' ' + l + ': ' + afpr(f(indiv))
			print outstr
		print ''

	def paretoWarning(self, paretoFront):
		# Warn user when the Pareto front gets too large
		r = float(len(paretoFront))/float(self.params['populationSize'])
		if r == 0.0:
			raise RuntimeError('No nondominated individuals!')
		if r > 0.75:
			print 'WARNING! Proportion of nondominated individuals too high (' + str(r) + ')'

	def findParetoFront(self, func0, func1, breakTiesByIDs=True, population=None):
		# The optional parameters are useful for bruteforce search algorithms
		if population is None:
			population = self.population
		for indiv in population:
			indiv.__dominated__ = False
		for ii in population:
			for ij in population:
				if not ii is ij and firstDominatedBySecond(ii, ij, func0, func1, breakTiesByIDs=breakTiesByIDs):
					ii.__dominated__ = True
		paretoFront = filter(lambda x: not x.__dominated__, population)
		return paretoFront

	def findParetoFrontManyObjectives(self, funcs, breakTiesByIDs=True, population=None):
		for indiv in self.population:
			indiv.__dominated__ = False
		for ii in self.population:
			for ij in self.population:
				if not ii is ij and firstDominatedBySecondManyObjectives(ii, ij, funcs):
#				if not ii is ij and firstStochasticallyDominatedBySecondManyObjectives(ii, ij, funcs, self.params['secondObjectiveProbability']):
					ii.__dominated__ = True
		paretoFront = filter(lambda x: not x.__dominated__, self.population)
		return paretoFront

	def findStochasticalParetoFront(self, func0, func1):
		for indiv in self.population:
			indiv.__dominated__ = False
		for ii in self.population:
			for ij in self.population:
				if not ii is ij and firstStochasticallyDominatedBySecond(ii, ij, func0, func1, self.params['secondObjectiveProbability']):
					ii.__dominated__ = True
#		for string in [ '{}, {} : {}'.format(str(indiv), str(indiv.score), str(indiv.__dominated__)) for indiv in self.population ]:
#			print(string)
#		print('')
		paretoFront = filter(lambda x: not x.__dominated__, self.population)
		if len(paretoFront) > 0:
			return paretoFront
		else:
			return self.findStochasticalParetoFront(func0, lambda x: 0.) # if the Pareto front came out empty, we sort with just the first objective & tie breaking

	def _logBestIndividual(self, filename=None):
		if not self._shouldIRunAPeriodicFunctionNow('logBestIndividual'):
			return
		if filename is None:
			filename = 'bestIndividual' + str(self.params['randomSeed']) + '.log'
		self._bestIndividualLogFileName = filename
		bestIndiv = self.population[-1]
		if self.logHeaderWritten:
			with open(filename, 'a') as logFile:
				logFile.write(str(self.generation) + ' ' + afpr(bestIndiv.score) + ' ' + str(bestIndiv) + '\n')
		else:
			with open(filename, 'w') as logFile:
				self._writeParamsToLog(logFile)
				logFile.write('# Columns: generation score ID indivDesc0 indivDesc1 ...\n')
			self.logHeaderWritten = True
			self._logBestIndividual(filename=filename)

	def _logPopulation(self, prefix='population'):
		if not self._shouldIRunAPeriodicFunctionNow('logPopulation'):
			return
		filename = prefix + '_gen' + str(self.generation) + '.log'
		with open(filename, 'w') as logFile:
			self._writeParamsToLog(logFile)
			logFile.write('# Columns: score ID indivDesc0 indivDesc1 ...\n')
			for indiv in self.population:
				logFile.write(afpr(indiv.score) + ' ' + str(indiv) + '\n')

	def _logConcatenatedPopulation(self, filename='population'):
		if not self.params.has_key('logConcatenatedPopulation') or not self.params['logConcatenatedPopulation']:
			return
		with open(filename, 'a') as logFile:
			if not hasattr(self, '__concatenatedPopulationLogStarted__') or not self.__concatenatedPopulationLogStarted__:
				self._writeParamsToLog(logFile)
				logFile.write('# Columns: score ID indivDesc0 indivDesc1 ...\n')
				self.__concatenatedPopulationLogStarted__ = True
			for indiv in self.population:
				logFile.write(afpr(indiv.score) + ' ' + str(indiv) + '\n')

	def logSubpopulation(self, subpopulation, prefix, inioption=None, genPostfix=True):
		'''Logs an arbitrary subpopulation.
         Arguments:
           subpopulation - subpopulation to log.
           prefix - the base name of output files.
           inioption - the name of the .ini option controlling the recording
             process. If None, recording occurs unconditionally.
           genPostfix - should the function append a postfix with a generation
             number to the file name? If False, the file will be overwritten on
             each call with the same prefix.
		'''
		if inioption and not self._shouldIRunAPeriodicFunctionNow(inioption):
			return
		filename = prefix
		if genPostfix:
		 filename += '_gen' + str(self.generation)
		filename += '.log'
		with open(filename, 'w') as logFile:
			self._writeParamsToLog(logFile)
			logFile.write('# Columns: score ID indivDesc0 indivDesc1 ...\n')
			for indiv in subpopulation:
				logFile.write(afpr(indiv.score) + ' ' + str(indiv) + '\n')

	def logParetoFront(self, paretoFront):
		if self.paramExists('logParetoFrontKeepAllGenerations'):
			keepAllGens = self.params['logParetoFrontKeepAllGenerations']
		else:
			keepAllGens = False
		self.logSubpopulation(paretoFront, 'paretoFront', inioption='logParetoFront', genPostfix=keepAllGens)

	def _writeParamsToLog(self, file):
		file.write('# Evolver parameters: ' + self._deterministicDict2Str(self.params) + '\n')
		file.write('# Individual parameters: ' + self._deterministicDict2Str(self.indivParams) + '\n')

	def _deterministicDict2Str(self, dict):
		pairStrs = [ '\'' + key + '\': ' + str(dict[key]) for key in sorted(dict.keys()) ]
		return '{' + ','.join(pairStrs) + '}'

	def noisifyAllScores(self):
		for indiv in self.population:
			indiv.noisifyScore(self.params['noiseAmplitude'])

	def populationIsValid(self):
		'''True iff the population is not oversized and all individuals belong to the correct class'''
		return len(self.population) <= self.params['populationSize'] and all([ type(indiv) == self.params['indivClass'] for indiv in self.population ])

	def _appendPopulationFromFile(self, filename):
		file = open(filename, 'r')
		for line in file:
			indiv = self.params['indivClass'](self.indivParams)
			indiv.fromStr(line)
			self.population.append(indiv)
		if not self.populationIsValid():
			raise ValueError('Inital population is too large')
		map(lambda x: x.recoverID(), self.population)   # make sure that we start from the next free ID

	def generateLogsAndStdout(self):
		# Config-dependent output functions: won't do anything unless the config contains explicit permission
		self._printGeneration()
		self._logBestIndividual(filename = 'bestIndividual' + str(self.params['randomSeed']) + '.log')
		self._logPopulation(prefix = 'population' + str(self.params['randomSeed']))
		self._logConcatenatedPopulation(filename = 'population' + str(self.params['randomSeed']) + '.log')
		self._printBestIndividual()
		self._printPopulation()

	def paramExists(self, paramName):
		return hasattr(self, 'params') and self.params.has_key(paramName)

	def paramIsEnabled(self, paramName):
		return self.paramExists(paramName) and self.params[paramName]

	def paramIsNonzero(self, paramName):
		return self.paramExists(paramName) and self.params[paramName] != 0.

	def _shouldIRunAPeriodicFunctionNow(self, paramName):
		if not self.paramIsEnabled(paramName):
			return False
		period = 1 if not self.params.has_key(paramName + 'Period') else self.params[paramName + 'Period']
		if not self.generation % period == 0:
			return False
		return True

	def setParamDefault(self, paramName, paramVal):
		if not self.params.has_key(paramName):
			self.params[paramName] = paramVal

	def globalGenerationCounterRequired(self):
		return self.paramIsEnabled('trackAncestry') or self.paramIsEnabled('globalGenerationCounter')

	# little dirty hack which exploits the fact that there's always just one Evolver to communicate generation number to Individuals
	def _createGlobalGenerationCounter(self):
		import __builtin__
		if self.globalGenerationCounterRequired():
			if not hasattr(__builtin__, 'globalGenerationCounter'):
				__builtin__.globalGenerationCounter = 0
			else:
				raise AttributeError('__builtin__ already has a globalGenerationCounter attribute, refusing to proceed')

	# second part of the hack
	def _setGlobalGenerationCounter(self):
		import __builtin__
		if self.globalGenerationCounterRequired():
			__builtin__.globalGenerationCounter = self.generation

