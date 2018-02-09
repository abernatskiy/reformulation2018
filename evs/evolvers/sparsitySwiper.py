import numpy as np
from copy import deepcopy
from baseEvolver import BaseEvolver

class Evolver(BaseEvolver):
	'''Not an evolutionary algorithm, but rather a 
     landscape investigation tool. It takes a range of 
     values of vector density (expressed as a total
     number of connections) as its parameter. Then 
     for each value k it constructs a population of 
     vectors with k nonzero values. This is performed by 
     calling the individuals constructor, then 
     setValuesToZero(), then calling insert() k times. 
     Works only with individuals.triVecAdvMut now.
     Methods and parameters:
       evolParams['populationSize'] - sample size, required
       evolParams['beginConn'] - initial value of k, default is 0
       evolParams['endConn'] - initial value of k, default is length of the vector
       evolParams['indivClass'].setValuesToZero()
       evolParams['indivClass'].insert()'''
	def __init__(self, communicator, indivParams, evolParams):
		super(Evolver, self).__init__(communicator, indivParams, evolParams)
		if self.params.has_key('beginConn'):
			self.generation = self.params['beginConn']
		else:
			self.params['beginConn'] = 0
		if not self.params.has_key('endConn'):
			self.params['endConn'] = indivParams['length']
		self.params['genStopAfter'] = self.params['endConn']
		self.indivParams = indivParams

		for i in xrange(self.params['populationSize']):
			indiv = self.params['indivClass'](self.indivParams)
			indiv.setValuesToZero()
			for j in xrange(self.generation):
				indiv.insert()
			self.population.append(indiv)
		self.communicator.evaluate(self.population)
		self.population.sort(key = lambda x: x.score)

	def optionalParametersTranslator(self):
		t = super(Evolver, self).optionalParametersTranslator()
		t['toInt'].update({'beginConn', 'endConn'})
		return t

	def updatePopulation(self):
		super(Evolver, self).updatePopulation()
		self.population = []
		for i in xrange(self.params['populationSize']):
			indiv = self.params['indivClass'](self.indivParams)
			indiv.setValuesToZero()
			for j in xrange(self.generation):
				indiv.insert()
			self.population.append(indiv)
		self.communicator.evaluate(self.population)
		self.population.sort(key = lambda x: x.score)
