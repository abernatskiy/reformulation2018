import numpy as np
from integerVector import Individual as IntegerVector

def inclusiveRange(lval, uval):
	return xrange(int(lval), int(uval)+1)

class Individual(IntegerVector):
	'''Base class for evolutionary individuals described by a vector of constant
     length composed of integers, with a single real-valued score. The values
     are taken from [initLowerLimit, initUpperLimit] upon the initialization
     and may change outside of these limits, but within [lowerCap, upperCap].

     The class has no mutation() method and therefore can only be used as a
     base class.

     Constructor takes a dictionary with the following parameter fields:
       length
       initLowerLimit, initUpperLimit

     Optional fields:
       lowerCap, upperCap
         (default -inf, inf; finite values required for bruteforce enumerations)
	'''
	def __init__(self, params):
		super(Individual, self).__init__(params)

		if not self.paramExists('lowerCap'):
			self.params['lowerCap'] = float('-Inf')
		if not self.paramExists('lowerCap'):
			self.params['upperCap'] = float('Inf')

		self.values = []
		for i in xrange(self.params['length']):
			self.values.append(self.getAnInitialValue())

	def requiredParametersTranslator(self):
		t = super(Individual, self).requiredParametersTranslator()
		t['toInt'].update({'initLowerLimit', 'initUpperLimit'})
		return t

	def optionalParametersTranslator(self):
		t = super(Individual, self).optionalParametersTranslator()
		t['toInt'].update({'lowerCap', 'upperCap', 'mutationAmplitude'})
		return t

	def getAnInitialValue(self):
		return np.random.choice(inclusiveRange(self.params['initLowerLimit'], self.params['initUpperLimit']))

	def changeWeight(self, pos):
		inc = np.random.choice(inclusiveRange(-1.*self.params['mutationAmplitude'], self.params['mutationAmplitude']))
		self.values[pos] = int(np.clip(self.values[pos] + inc, self.params['lowerCap'], self.params['upperCap']))

	def setValuesToTheFirstSet(self):
		if not np.isfinite(self.params['lowerCap']) or not np.isfinite(self.params['upperCap']):
			raise ValueError('Caps must be specified to use setValuesToTheFirstSet()')

		for i in xrange(self.params['length']):
			self.values[i] = self.params['lowerCap']

	def increment(self):
		if not np.isfinite(self.params['lowerCap']) or not np.isfinite(self.params['upperCap']):
			raise ValueError('Caps must be specified to use increment()')

		lcap = self.params['lowerCap']
		ucap = self.params['upperCap']
		base = ucap-lcap+1

		if not hasattr(self, '__incrementCalled__') or not self.__incrementCalled__:
			self.__incrementCalled__ = True
			ssize = base**self.params['length']
			print 'Brute force search attempted on the space of ' + str(ssize) + ' individuals.'
			if ssize > 10**8:
				print 'WARNING! This is madness.'

		self.renewID() # we start with it because it is inevitable

		numRepr = 0
		order = 0
		for val in self.values:
			numRepr += (val-lcap)*(base**order)
			order += 1

		numRepr += 1

		if numRepr / (base**order) >= 1:
			self.setValuesToTheFirstSet()
			return False

		while order > 0:
			order -= 1
			curDig = numRepr / (base**order)
			numRepr -= curDig*(base**order)
			self.values[order] = lcap + curDig

		return True
