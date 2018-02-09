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
        If 'sparse' is chosen, the following
        method is required:
       evolParams['indivClass'].setValuesToZero().
     NOTE: unlike AFPO, this method does not work
     too well with probability-1 mutations'''
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
		self.noisifyAllScores()
		for indiv in self.population:
			indiv.score = 0 if indiv.score < 0 else indiv.score
		self.population.sort(key = lambda x: x.score)

	def updatePopulation(self):
		super(Evolver, self).updatePopulation()
		weights = np.array(map(lambda x: x.score, self.population), dtype=np.float)
#		print "Weights: " + str(weights)
#		print "Sum: " + str(weights.sum())
		if weights.sum() == 0.0:
			print("Warning: ProportionalEvolver: no fit individuals, zero-sum scores, selecting the ancestors equiprobably")
			weights = np.ones(len(weights))/len(weights)
		else:
			weights = weights/weights.sum()
		newPopulation = []
		while len(newPopulation) < self.params['populationSize']:
			parent = np.random.choice(self.population, p=weights)
			child = deepcopy(parent)
			child.mutate()
			newPopulation.append(child)
		self.population = newPopulation
		self.communicator.evaluate(self.population)
		self.noisifyAllScores()
		for indiv in self.population:
			indiv.score = 0 if indiv.score < 0 else indiv.score
		self.population.sort(key = lambda x: x.score)
