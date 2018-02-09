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
	if indiv0.score == indiv1.score:
		if indiv0.age == indiv1.age:
			return indiv0.id < indiv1.id
		else:
			return indiv0.age > indiv1.age
	else:
		return indiv0.score < indiv1.score and indiv0.age >= indiv1.age

class Evolver(BaseEvolver):
	'''AFPO (Age-Fitness Pareto Optimization) - evolutionary algorithm
     which uses age of individuals to maintain diversity. The age is
     defined as the number of generations this individual has spent
     within the population. Less fit individual is considered to be
     as valuable as the more fit one if it is younger. Required
     methods and parameters, aside from the common set:
       evolParams['populationSize']'''
	def __init__(self, communicator, indivParams, evolParams, initialPopulationFileName = None):
		super(Evolver, self).__init__(communicator, indivParams, evolParams, initialPopulationFileName = initialPopulationFileName)
		while len(self.population) < self.params['populationSize']:
			indiv = self.params['indivClass'](self.indivParams)
			self.population.append(indiv)
		for indiv in self.population:
			indiv.age = 0
		self.communicator.evaluate(self.population)

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

		if self.params.has_key('printParetoFront') and self.params['printParetoFront'] == 'yes':
			for indiv in paretoFront:
				print str(indiv) + ' score: ' + str(indiv.score) + ' age: ' + str(indiv.age)
			print ''

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

		self.communicator.evaluate(mutated)
		self.population = paretoFront + mutated
		self.population.sort(key = lambda x: x.score)

	def printBestIndividual(self):
		bestIndiv = self.population[-1]
		print 'Best individual: ' + str(bestIndiv) + ' score: ' + str(bestIndiv.score) + ' age: ' + str(bestIndiv.age)

	def printPopulation(self):
		print '----------'
		for indiv in self.population:
			print str(indiv) + ' score: ' + str(indiv.score) + ' age: ' + str(indiv.age)
		print ''
