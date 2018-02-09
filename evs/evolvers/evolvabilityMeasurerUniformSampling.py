import numpy as np
from copy import deepcopy
from baseEvolver import BaseEvolver

class Evolver(BaseEvolver):
	'''An evolutionary algorithm dummy which 
     facilitates the measurement of the 
     evolvability. To this end, it creates a 
     generation of randomly generated genomes, 
     evaluates them, then mutates each one once 
     and evaluates the resulting population.
     Required methods and parameters:
       evolParams['populationSize']
     NOTE1: do not use the logBestIndividual 
     option with this evolver'''
	def __init__(self, communicator, indivParams, evolParams, initialPopulationFileName = None):
		super(Evolver, self).__init__(communicator, indivParams, evolParams, initialPopulationFileName = initialPopulationFileName)
		while len(self.population) < self.params['populationSize']:
			indiv = self.params['indivClass'](indivParams)
			self.population.append(indiv)
		self.params['genStopAfter'] = 1
		self.communicator.evaluate(self.population)

	def updatePopulation(self):
		super(Evolver, self).updatePopulation()
		for indiv in self.population:
			indiv.mutate()
		self.communicator.evaluate(self.population)
