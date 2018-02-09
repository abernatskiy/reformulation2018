from copy import deepcopy
from proportionalEvolver import Evolver as ProportionalEvolver

class Evolver(ProportionalEvolver):
	'''Proportional evover with the initial population 
     formed as in Espinosa-Soto Wagner 2010. Unlikely 
     to work with any Individuals other than those 
     implemented in individuals.triVecESW.'''
	def __init__(self, communicator, indivParams, evolParams):
		super(ProportionalEvolver, self).__init__(communicator, indivParams, evolParams)
		baseIndiv = self.params['indivClass'](indivParams)
		baseIndiv.initSparse()
		for i in xrange(self.params['populationSize']):
			indiv = deepcopy(baseIndiv)
			indiv.mutate()
			self.population.append(indiv)
		self.communicator.evaluate(self.population)
