from copy import deepcopy
from baseEvolver import BaseEvolver
import numpy as np

class Evolver(BaseEvolver):
	'''Minimal Diversity-Preserving Evolutionary Algorithm
       Every generation consists of three individuals:
        - the champion of the previous generation;
        - its mutated version;
        - random genome.
       Required methods and parameters:
        communicator.evaluate(population)
        evolParams['indivClass']
        evolParams['indivClass'].mutate()'''
	def __init__(self, communicator, indivParams, evolParams):
		super(Evolver, self).__init__(communicator, indivParams, evolParams)
		class ConnectionCostIndividuals(self.params['indivClass']):
			def numConnections(self):
				return np.count_nonzero(self.values)
			def __lt__(self, other):
				return (self.score - self.params['connectionCost']*self.numConnections()) < (other.score - other.params['connectionCost']*other.numConnections())
		self.params['indivClass'] = ConnectionCostIndividuals
		for i in xrange(3):
			indiv = self.params['indivClass'](indivParams)
			self.population.append(indiv)
		self.communicator.evaluate(self.population)

	def updatePopulation(self):
		super(Evolver, self).updatePopulation()
		bestIndiv = self.population[-1]
		self.population = []

		mutatedIndiv = deepcopy(bestIndiv)
		while not mutatedIndiv.mutate():
			pass
		self.population.append(mutatedIndiv)
		
		randomIndiv = self.params['indivClass'](bestIndiv.params)
		self.population.append(randomIndiv)

		self.communicator.evaluate(self.population)

		self.population.append(bestIndiv)
		self.population.sort()
