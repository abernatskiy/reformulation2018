import numpy as np
import __builtin__

from collections import deque
from copy import deepcopy
from cluneSimplified import Evolver as CluneSimplifiedEvolver

class Memory(object):
	'''A FIFO data structure that holds a fixed number of entries.
     If more entries are added, the oldest ones are removed.
     It can also check if all the entries in it are the same.
	'''
	def __init__(self, numElements):
		self.n = numElements
		self.q = deque()

	def push(self, newElem):
		self.q.append(newElem)
		while len(self.q) > self.n:
			self.q.popleft()

	def uniform(self):
		return self.n == len(self.q) and self.q.count(self.q[0]) == len(self.q)

	def clear(self):
		self.q.clear()

class Evolver(CluneSimplifiedEvolver):
	'''Experimental class, all info below is probably obsolete by now, use source.

     A variant of connection cost-based multiobjective selection algorithm that
     also protects morphologies while their controllers are optimized.

     The only difference in using this one is that unlike the cluneSimplified
     it always (and not for certain settings of parameters) expects all
     Individuals to be composites of two: morphology (Class0) and controller
     (Class1 in configs of the composite).

     Below is a copy of the cluneSimplified docstring.

     Multiobjective algorithm which minimizes the connection cost alongside
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
		self.setParamDefault('initialTimeEstimateCoefficient', 3.)
		self.setParamDefault('initialTimeEstimatePower', 1)
		__builtin__.timeEstimateCoefficient = self.params['initialTimeEstimateCoefficient']
		__builtin__.timeEstimatePower = self.params['initialTimeEstimatePower']

		self.setParamDefault('memorySize', 100)
		self.fitnessTS = Memory(self.params['memorySize'])

		self.increases = 0

	def requiredParametersTranslator(self):
		t = super(Evolver, self).requiredParametersTranslator()
		t['toFloat'].update(['initialTimeEstimateCoefficient', 'initialTimeEstimatePower'])
		t['toInt'].update(['memorySize'])
		return t

#	def getConnectionCostFunc(self):
#		self.secondObjectiveLabel = 'connection cost'
#		return len(filter(lambda y: y!=0, x.parts[1].values))

	def updatePopulation(self):
		self.fitnessTS.push(self.population[-1].score)
		if self.fitnessTS.uniform():
			self.increases += 1

			if (self.increases % 5) == 0:
				__builtin__.timeEstimatePower *= 2.
			else:
				__builtin__.timeEstimateCoefficient *= 2.
			print('Time estimate increased for the ' + str(self.increases) + 'th time! New formula is ' + str(__builtin__.timeEstimateCoefficient) + '*CC^' + str(__builtin__.timeEstimatePower))

			self.params['memorySize'] *= 2
			self.fitnessTS = Memory(self.params['memorySize'])
		super(Evolver, self).updatePopulation()
