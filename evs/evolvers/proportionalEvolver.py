import numpy as np
from copy import deepcopy
from baseEvolver import BaseEvolver

class Evolver(BaseEvolver):
	'''Evolutionary algorithm in which every 
     inidividual of the next generation is a 
     mutant of an individual of the current 
     generation, selected at random with 
     probability propotional to its fitness.
     Required methods and parameters:
       evolParams['populationSize']
       evolParams['initialPopulationType']
        - can be 'random' or 'sparse'.
        Defaults to 'random'.
        If 'sparse' is chosen, the following
        method is required:
       evolParams['indivClass'].setValuesToZero().
       evolParams['eliteSize']
     NOTE: unlike AFPO, this method does not work
     too well with probability-1 mutations'''
	def __init__(self, communicator, indivParams, evolParams, initialPopulationFileName = None):
		super(Evolver, self).__init__(communicator, indivParams, evolParams, initialPopulationFileName = initialPopulationFileName)
		while len(self.population) < self.params['populationSize']:
			indiv = self.params['indivClass'](indivParams)
			if not self.params.has_key('initialPopulationType') or self.params['initialPopulationType'] == 'random':
				pass
			elif self.params['initialPopulationType'] == 'sparse':
				indiv.setValuesToZero()
				indiv.mutate()
			else:
				raise ValueError('Wrong type of initial population')
			self.population.append(indiv)
		self.communicator.evaluate(self.population)
		self.population.sort(key = lambda x: x.score)

	def optionalParametersTranslator(self):
		t = super(Evolver, self).optionalParametersTranslator()
		t['toInt'].add('eliteSize')
		return t

	def updatePopulation(self):
		super(Evolver, self).updatePopulation()
		weights = np.array(map(lambda x: x.score, self.population), dtype=np.float)
		if weights.sum() == 0.0:
			print("Warning: ProportionalEvolver: no fit individuals, zero-sum scores, selecting the ancestors equiprobably")
			weights = np.ones(len(weights))/len(weights)
		else:
			weights = weights/weights.sum()
		if self.params.has_key('eliteSize'):
			newPopulation = self.population[-1*self.params['eliteSize']:]
		else:
			newPopulation = []
		while len(newPopulation) < self.params['populationSize']:
			parent = np.random.choice(self.population, p=weights)
			child = deepcopy(parent)
			child.mutate()
			newPopulation.append(child)
		self.population = newPopulation
		self.communicator.evaluate(self.population)
		self.population.sort(key = lambda x: x.score)
