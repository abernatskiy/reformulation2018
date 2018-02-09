import numpy as np
from copy import deepcopy
from baseEvolver import BaseEvolver

def firstDominatedBySecond(indiv0, indiv1):
	# truth table:
	#              i0.f<i1.f    i0.f=i1.f    i0.f>i1.f
	# i0.a<i1.a    F            F            F
	# i0.a=i1.a    T            by ID        F
	# i0.a>i1.a    T            T            F
	if indiv0.id == indiv1.id:
		raise RuntimeError('AFPO: Two individuals with the same ID compared')
	if indiv0.cma == indiv1.cma:
		if indiv0.age == indiv1.age:
			return indiv0.id < indiv1.id
		else:
			return indiv0.age > indiv1.age
	else:
		return indiv0.cma < indiv1.cma and indiv0.age >= indiv1.age

class Evolver(BaseEvolver):
	'''Doubtful AFPO (Age-Fitness Pareto Optimization) - 
     evolutionary algorithm for noisy clients,
     which uses age of individuals to maintain diversity. The age is
     defined as the number of generations this individual has spent
     within the population. Less fit individual is considered to be
     as valuable as the more fit one if it is younger. 
     The number of times an evaluation is taken from the client is 
     equal to individual's age; an average of all readings is taken 
     to be the individual's fitness at every generation. Required
     methods and parameters, aside from the common set:
       evolParams['populationSize']'''
	def __init__(self, communicator, indivParams, evolParams):
		super(Evolver, self).__init__(communicator, indivParams, evolParams)
		self.indivParams = indivParams
		for i in xrange(self.params['populationSize']):
			indiv = self.params['indivClass'](self.indivParams)
			indiv.age = 0
			self.population.append(indiv)
		self.__evaluateWithDoubt__(self.population)

	def __evaluateWithDoubt__(self, population):
		for indiv in population:
			if not hasattr(indiv, 'cma'):
				indiv.cma = 0.0
				indiv.noOfMeasurements = 0
		self.communicator.evaluate(population)
		for indiv in population:
			indiv.cma = (indiv.score + indiv.cma*indiv.noOfMeasurements)/(indiv.noOfMeasurements + 1)
			indiv.noOfMeasurements += 1

	def updatePopulation(self):
		super(Evolver, self).updatePopulation()

		# finding Pareto front
		for indiv in self.population:
			indiv.__dominated__ = False
		for i in xrange(self.params['populationSize']):
			for j in xrange(self.params['populationSize']):
				if i != j and firstDominatedBySecond(self.population[i], self.population[j]):
					self.population[i].__dominated__ = True
		paretoFront = []
		for indiv in self.population:
			if not indiv.__dominated__:
				paretoFront.append(indiv)

		# debug messages
#		paretoFront.sort(key = lambda x: x.score)
#		self.population = paretoFront
#		print 'Pareto front:'
#		self.printPopulation()

		# increasing age for all nondominated individuals
		for indiv in paretoFront:
			indiv.age += 1

		# a useful warning
		r = float(len(paretoFront))/float(self.params['populationSize'])
		if r == 0.0:
			raise RuntimeError('No nondominated individuals!')
		if r > 0.75:
			print 'WARNING! Proportion of nondominated individuals too high (' + str(r) + ')'

		# forming offsprings
		mutated = []
		while len(mutated) < self.params['populationSize'] - len(paretoFront) - 1:
			newIndiv = deepcopy(np.random.choice(paretoFront))
			if newIndiv.mutate():
				mutated.append(newIndiv)

		# injecting a random individual
		if len(paretoFront) < self.params['populationSize']:
			mutated.append(self.params['indivClass'](self.indivParams))
			mutated[-1].age = 0

		self.population = paretoFront + mutated
		self.__evaluateWithDoubt__(self.population)
		self.population.sort(key = lambda x: x.score)

	def printBestIndividual(self):
		bestIndiv = self.population[-1]
		print 'Best individual: ' + str(bestIndiv) + ' avg score: ' + str(bestIndiv.cma) + ' age: ' + str(bestIndiv.age)

	def printPopulation(self):
		print '----------'
		for indiv in self.population:
			print str(indiv) + ' avg score: ' + str(indiv.cma) + ' age: ' + str(indiv.age)
		print ''
