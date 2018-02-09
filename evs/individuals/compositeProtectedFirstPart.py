import numpy as np
import math
import __builtin__

from compositeFixedProbabilities import Individual as CompositeFixedProbabilitiesIndividual

                                                                                
class Individual(CompositeFixedProbabilitiesIndividual):
	'''Composite of individuals of exactly two Individual classes in which the
     first Individual is protected from mutating before the second one
     experiences a sufficient number of mutations.
	'''
	def __init__(self, params):
		super(Individual, self).__init__(params)
		if len(self.partClasses) != 2:
			raise ValueError('Only two class composites are supported by compositeProtectedFirstPart, requested creations of a composite of ' + str(len(self.partClasses)) + ' classes')
		self.timeOfLastMorphologicalMutation = __builtin__.globalGenerationCounter
		self.setParamDefault('timeEstimateCoefficient', 3.)
		self.setParamDefault('timeEstimatePower', 1)
		self.setParamDefault('timeEstimateWidth', 1.)

	def _extractMutationProbabilities(self):
		pass

	def optionalParametersTranslator(self):
		t = super(Individual, self).optionalParametersTranslator()
		t['toFloat'].remove('^probabilityOfMutatingClass[0-9]+$')
		t['toFloat'].update(['timeEstimateCoefficient', 'timeEstimatePower', 'timeEstimatePower', 'timeEstimateWidth'])
		return t

	def controllerTimeLimit(self):
		connectionCost = len(filter(lambda x: x!=0, self.parts[1].values))
		return self.params['timeEstimateCoefficient']*np.power(float(connectionCost), self.params['timeEstimatePower'])

	def probabilityOfMorphologicalMutation(self):
		tsmm = __builtin__.globalGenerationCounter - self.timeOfLastMorphologicalMutation
		return 1./ (1. + np.exp((self.controllerTimeLimit() - tsmm)/self.params['timeEstimateWidth']))

	def mutate(self):
		roll = np.random.random()
		if roll < self.probabilityOfMorphologicalMutation():
			if self.parts[0].mutate():
				self.renewID()
				self.timeOfLastMorphologicalMutation = __builtin__.globalGenerationCounter
				return True
		else:
			if self.parts[1].mutate():
				self.renewID()
				return True
		return False
