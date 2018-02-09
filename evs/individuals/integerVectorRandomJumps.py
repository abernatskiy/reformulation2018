import numpy as np
from integerVectorBounded import Individual as IntegerVectorBounded

class Individual(IntegerVectorBounded):
	'''Class for evolutionary individuals described by a vector of constant length
     composed of integers, with a single real-valued score. The values are taken
     from [initLowerLimit, initUpperLimit] upon the initialization.

     The mutation is a random jump in the genotype space, i.e. each mutation
     regenerates the values from scratch.

     Constructor takes a dictionary with the following parameter fields:
       length
       initLowerLimit, initUpperLimit

     Optional fields:
       mutationAmplitude (default 1)
       initProbabilityOfConnection (default 1) -
         provides a mechanism for generating sparse networks.
	'''
	def optionalParametersTranslator(self):
		t = super(Individual, self).optionalParametersTranslator()
		t['toInt'].remove('lowerCap')
		t['toInt'].remove('upperCap')
		return t

	def mutate(self):
		self.values = []
		for i in xrange(self.params['length']):
			self.values.append(self.getAnInitialValue())
		self.renewID()
		return True
