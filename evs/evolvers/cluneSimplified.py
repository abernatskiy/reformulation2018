import numpy as np
from copy import deepcopy
from baseEvolver import BaseEvolver

class Evolver(BaseEvolver):
	'''Multiobjective algorithm which minimizes the connection cost alongside
     with maximizing the fitness function. It is similar to the technique used
     in the 2013 Clune Mouret Lipson "The evolutionary origins of modularity"
     paper; the difference is that instead of using NSGA-II, we simply keep the
     whole Pareto front at each generation and add its offsprings to the
     population until it restores its size.

     Required parameters:
       evolParams['populationSize']
       evolParams['initialPopulationType'] - can be 'random' or 'sparse'.
         If 'sparse' is chosen, the initial population will be composed of
         individulas with all genes set to zero and mutated once. To do so,
         the algorithm will use the following method of the individual class:
           evolParams['indivClass'].setValuesToZero().
         Feel free to use it to redefine the meaning of the sparsity!
         More info on benefits of sparse initial populations can be found in
         2015 Bernatskiy Bongard "Exploiting the relationship between structural
         modularity and sparsity for faster network evolution".

     Optional parameters:
       evolParams['secondObjectiveProbability'] - if provided, connection cost
         will only be taken into account with the specified probability. If it
         is not taken into account, the algorithm will assume that the
         individual with larger fitness dominates regardless of connection cost.
         See 2013 Clune et al.
       evolParams['useMaskForSparsity'] - use mask instead of comparing the
         fields to zero to count nonzero values.
       evolParams['noiseAmplitude'] - if provided, noisy evaluations with a
			  uniformly distributed noise of given amplitude will be simulated.

     NOTE: Individual classes with surefire mutation operator are OK.'''

	def __init__(self, communicator, indivParams, evolParams, initialPopulationFileName = None):
		super(Evolver, self).__init__(communicator, indivParams, evolParams, initialPopulationFileName=initialPopulationFileName)
		if self.params['initialPopulationType'] == 'random':
			while len(self.population) < self.params['populationSize']:
				indiv = self.getRandomIndividual()
				self.population.append(indiv)
		elif self.params['initialPopulationType'] == 'sparse':
			while len(self.population) < self.params['populationSize']:
				indiv = self.getSparseIndividual()
				self.population.append(indiv)
		elif self.params['initialPopulationType'] == 'expandFromFile':
			if not initialPopulationFileName:
				raise ValueError('Initial population file name must be specified if initialPopulationType=expandFromFile is used')
			curPopLen = len(self.population)
			while len(self.population) < self.params['populationSize']:
				indiv = deepcopy(np.random.choice(self.population[:curPopLen]))
				indiv.mutate()
				self.population.append(indiv)
		else:
			raise ValueError('Wrong type of initial population')
		self.communicator.evaluate(self.population)
		self.population.sort(key = lambda x: x.score)
		self.paretoFront = self.getCluneParetoFront()

		self.paretoSizeHeaderWritten = False

	def getRandomIndividual(self):
		return self.params['indivClass'](self.indivParams)

	def getSparseIndividual(self):
		indiv = self.params['indivClass'](self.indivParams)
		indiv.setValuesToZero()
		indiv.mutate()
		return indiv

	def requiredParametersTranslator(self):
		t = super(Evolver, self).requiredParametersTranslator()
		t['toFloat'].add('secondObjectiveProbability')
		t['toString'].add('initialPopulationType')
		return t

	def optionalParametersTranslator(self):
		t = super(Evolver, self).optionalParametersTranslator()
		t['toFloat'].remove('secondObjectiveProbability')
		t['toBool'].add('useMaskForSparsity')
		return t

	def getConnectionCostFunc(self):
		if self.paramIsEnabled('useMaskForSparsity'):
			connectionCostFunc = lambda x: len(filter(lambda y: y, x.mask))
		else:
			connectionCostFunc = lambda x: len(filter(lambda y: y!=0, x.values))
		self.secondObjectiveLabel = 'connection cost'
		return connectionCostFunc

	def getErrorFunc(self):
		return lambda x: -1.*x.score

	def getCluneParetoFront(self):
		errorFunc = self.getErrorFunc()
		connectionCostFunc = self.getConnectionCostFunc()
		if self.paramExists('secondObjectiveProbability') and self.params['secondObjectiveProbability'] != 1.:
			return self.findStochasticalParetoFront(errorFunc, connectionCostFunc)
		else:
			return self.findParetoFront(errorFunc, connectionCostFunc)

	def logParetoSize(self, paretoFront):
		if not self._shouldIRunAPeriodicFunctionNow('logParetoSize'):
			return
		filename = 'paretoSize{}.log'.format(self.params['randomSeed'])
		if self.paretoSizeHeaderWritten:
			with open(filename, 'a') as logFile:
				logFile.write('{} {}\n'.format(self.generation, len(paretoFront)))
		else:
			with open(filename, 'w') as logFile:
				self._writeParamsToLog(logFile)
				logFile.write('# Columns: generation paretoFrontSize\n')
			self.paretoSizeHeaderWritten = True
			self.logParetoSize(paretoFront)

	def doParetoOutput(self):
		self.printParetoFront(self.paretoFront, self.secondObjectiveLabel, self.getConnectionCostFunc())
		self.logParetoFront(self.paretoFront)
		self.paretoWarning(self.paretoFront)
		self.logParetoSize(self.paretoFront)

	def processMutatedChild(self, child, parent):
		pass

	def generateLogsAndStdout(self):
		super(Evolver, self).generateLogsAndStdout()
		self.doParetoOutput()

	def updatePopulation(self):
		super(Evolver, self).updatePopulation()

		newPopulation = []
		while len(newPopulation)+len(self.paretoFront) < self.params['populationSize']:
			parent = np.random.choice(self.paretoFront)
			child = deepcopy(parent)
			child.mutate()
			self.processMutatedChild(child, parent)
			newPopulation.append(child)
		self.communicator.evaluate(newPopulation)
		self.population = newPopulation + self.paretoFront
		if self.paramExists('noiseAmplitude'):
			self.noisifyAllScores()
		self.population.sort(key = lambda x: x.score)
		self.paretoFront = self.getCluneParetoFront()
