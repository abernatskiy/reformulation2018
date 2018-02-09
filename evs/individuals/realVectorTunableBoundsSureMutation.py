import numpy as np
from realVector import Individual as RealVector

class Individual(RealVector):
	'''Class for evolutionary individuals described by a vector of
     real numbers taken from [initLowerLimit, initUpperLimit]
     of constant length, with a single-valued score represented
     by a real number. The default mode of mutation is to increase
     a randomly chosen number from the vector by a normally
     distributed, zero-centered random number. The width of the
     normal distribution is equal to the number itself times the
     relativeMutationAmplitude parameter. If variables lowerCap
     or upperCap are defined, the result is clipped to the range
     [lowerCap, upperCap].
     Constructor takes a dictionary with the following parameter
     fields:
       initLowerLimit, initUpperLimit
       relativeMutationAmplitude
       length                         - length of the vector
     Optional fields:
       lowerCap, upperCap
	'''
	def __init__(self, params):
		super(Individual, self).__init__(params)

		if not self.params.has_key('lowerCap'):
			self.params['lowerCap'] = float('-Inf')
		if not self.params.has_key('upperCap'):
			self.params['upperCap'] = float('Inf')

		self.values = []
		for i in xrange(self.params['length']):
			self.values.append(self.getAnInitialValue())

	def requiredParametersTranslator(self):
		t = super(Individual, self).requiredParametersTranslator()
		t['toFloat'].update({'initLowerLimit', 'initUpperLimit', 'relativeMutationAmplitude'})
		return t

	def optionalParametersTranslator(self):
		t = super(Individual, self).optionalParametersTranslator()
		t['toFloat'].update({'lowerCap', 'upperCap'})
		return t

	def getAnInitialValue(self):
		return self.params['initLowerLimit'] + (self.params['initUpperLimit'] - self.params['initLowerLimit'])*np.random.random()

	def changeWeight(self, pos):
		self.values[pos] *= (1. + self.params['relativeMutationAmplitude']*np.random.standard_normal())
		self.values[pos] = np.clip(self.values[pos], self.params['lowerCap'], self.params['upperCap'])

	def mutate(self):
		mutPos = np.random.random_integers(0, self.values.size-1)
		self.changeWeight(mutPos)
		self.renewID()
		return True

	def setValuesToTheFirstSet(self):
		for i in xrange(self.params['length']):
			self.values[i] = self.params['lowerCap']
