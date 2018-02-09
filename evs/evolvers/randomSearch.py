import numpy as np
from copy import deepcopy
from baseEvolver import BaseEvolver

class Evolver(BaseEvolver):
	'''An evolutionary algorithm dummy which 
     performs a random search by sampling 
     evolParams['populationSize'] genomes at 
     random.
	'''
	def __init__(self, communicator, indivParams, evolParams, initialPopulationFileName = None):
		super(Evolver, self).__init__(communicator, indivParams, evolParams, initialPopulationFileName = initialPopulationFileName)
		while len(self.population) < self.params['populationSize']:
			indiv = self.params['indivClass'](indivParams)
			self.population.append(indiv)
		self.params['genStopAfter'] = 0
		self.communicator.evaluate(self.population)
