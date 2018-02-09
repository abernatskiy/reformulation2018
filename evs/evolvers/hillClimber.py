from copy import deepcopy
from baseEvolver import BaseEvolver

class Evolver(BaseEvolver):
	'''Parallel Hill Climber - evolutionary algorithm which, 
     at every step, adds a mutated copy of its population to 
     the original population and shrinks the new population to 
     the former size by preserving fittest individuals. Required 
     methods and parameters:
       communicator.evaluate(population)
       evolParams['indivClass']
       evolParams['indivClass'].mutate()
       evolParams['populationSize']'''
	def __init__(self, communicator, indivParams, evolParams):
		super(Evolver, self).__init__(communicator, indivParams, evolParams)
		for i in xrange(self.params['populationSize']):
			indiv = self.params['indivClass'](indivParams)
			self.population.append(indiv)
		self.communicator.evaluate(self.population)

	def updatePopulation(self):
		super(Evolver, self).updatePopulation()

		newPopulation = deepcopy(self.population)
		for newIndiv in newPopulation:
			newIndiv.mutate()
		self.communicator.evaluate(newPopulation)
		self.population += newPopulation
		self.population.sort()
		# uniquifying the new population
		newPopulation = []
		for indiv in self.population:
			if indiv not in newPopulation:
				newPopulation.append(indiv)
		self.population = newPopulation
		# taking the tail
		self.population = self.population[-self.params['populationSize']:]
