import numpy as np
import math
import __builtin__

from compositeFixedProbabilities import Individual as CompositeFixedProbabilitiesIndividual

class Individual(CompositeFixedProbabilitiesIndividual):
	'''Composite of individuals of exactly two Individual classes designated for
     robot's morphology (first class) and control (second class).
     Tracks time of the last morphological mutation.
	'''
	def __init__(self, params):
		super(Individual, self).__init__(params)
		if len(self.partClasses) != 2:
			raise ValueError('Only two class composites are supported by morphologyControl, requested creations of a composite of ' + str(len(self.partClasses)) + ' classes')
		self.timeOfLastMorphologicalMutation = __builtin__.globalGenerationCounter

	def probabilityOfMorphologicalMutation(self):
		return self.params['probabilityOfMutatingClass0']

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
