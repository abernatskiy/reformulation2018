import numpy as np
from integerVectorBounded import Individual as IntegerVectorBounded

class Individual(IntegerVectorBounded):
	'''Class for evolutionary individuals described by a vector of constant length
     composed of integers, with a single real-valued score. The values are taken
     from [initLowerLimit, initUpperLimit] upon the initialization and may
     change outside of these limits, but within [lowerCap, upperCap].

     The mutation is a simple change of the weight of a randomly chosen
     connection (including the missing ones) by a random value taken from
     {-mutationAmplitude, -mutationAmplitude+1, ..., mutationAmplitude}. If the
     changed value lands outside of [lowerCap, upperCap], it is cropped. If the
     mutation results in no change, the same procedure is applied again until
     there is change.

     Constructor takes a dictionary with the following parameter fields:
       length
       initLowerLimit, initUpperLimit

     Optional fields:
       mutationAmplitude (default 1)
       lowerCap, upperCap
         (default -inf, inf; required for bruteforce enumerations)
	'''
	def __init__(self, params):
		super(Individual, self).__init__(params)
		self.setParamDefault('mutationAmplitude', 1)

	def optionalParametersTranslator(self):
		t = super(Individual, self).optionalParametersTranslator()
		t['toInt'].add('mutationAmplitude')
		return t

	def mutate(self):
		pos = np.random.choice(self.params['length'])
		oldWeight = self.values[pos]
		self.changeWeight(pos)
		if self.values[pos] != oldWeight:
			self.renewID()
			return True
		else:
			return self.mutate()
