import numpy as np
from copy import deepcopy
from baseEvolver import BaseEvolver

class Evolver(BaseEvolver):
	'''Multiobjective algorithm which optimizes age
       evolParams['populationSize']
       evolParams['initialPopulationType']
        - can be 'random' or 'sparse'.
        If 'sparse' is chosen, the following
        method is required:
       evolParams['indivClass'].setValuesToZero().'''
	def __init__(self, communicator, indivParams, evolParams):
		super(Evolver, self).__init__(communicator, indivParams, evolParams)
		if self.params['initialPopulationType'] == 'random':
			for i in xrange(self.params['populationSize']):
				indiv = self.params['indivClass'](indivParams)
				self.population.append(indiv)
		elif self.params['initialPopulationType'] == 'sparse':
		  for i in xrange(self.params['populationSize']):
				indiv = self.params['indivClass'](indivParams)
				indiv.setValuesToZero()
				indiv.mutate()
				self.population.append(indiv)
		else:
			raise ValueError('Wrong type of initial population')
		self.communicator.evaluate(self.population)
		self.population.sort(key = lambda x: x.score)
		for indiv in self.population:
			indiv.age = 0

	def updatePopulation(self):
		super(Evolver, self).updatePopulation()
		paretoFront = self.findParetoFront(lambda x: -1*x.score, lambda x: x.age)

		self.printParetoFront(paretoFront, 'time since mutation', lambda x: x.age)
		self.paretoWarning(paretoFront)

		newPopulation = []
		for indiv in paretoFront:
			newPopulation.append(indiv)
		while len(newPopulation) < self.params['populationSize']:
			parent = np.random.choice(paretoFront)
			child = deepcopy(parent)
			child.mutate()
			child.age = 0
			newPopulation.append(child)
		self.population = newPopulation
		self.communicator.evaluate(self.population)
		self.population.sort(key = lambda x: x.score)
		for indiv in self.population:
			indiv.age += 1
