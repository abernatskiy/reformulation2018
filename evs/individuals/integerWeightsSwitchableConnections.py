import numpy as np
from realWeightsSwitchableConnections import Individual as RealWeightsSwitchableConnections

def inclusiveRange(lval, uval):
	return map(float, xrange(int(lval), int(uval)+1))

class Individual(RealWeightsSwitchableConnections):
	'''Class for evolutionary individuals described by a vector of constant length
     composed of integer-valued weights, with a single real-valued score. The
     values are taken from [initLowerLimit, initUpperLimit] upon the
     initialization and may change outside of these limits, but within
     [lowerCap, upperCap].

     The integers are internally represented as floating point numbers. This may
     reflect on the Individuals' string representations.

     This class keeps track of which weights are zero and which
     are not using a member function isAZeroWeight(self, pos). This
     information is stored at self.map for use in mutation and
     connection cost computations.

     The mutation proceeds as follows:
      - With probability of mutExploration, the mutation operator
        will to attempt increase a randomly picked nonzero weight
        by a number randomly selected from
        [-mutationAmplitude, -mutationAmplitude+1, ... , mutationAmplitude]
        If the result ends up being a zero, the connection
        is removed. If the result is out of the interval
        [lowerCap, upperCap], it is clipped to fit the interval.
        If there are no connections to pick from, the mutation process
        starts over.
      - All other cases are divided between the insertions and
        deletions. Ratio of the frequencies is controlled by the
        mutInsDelRatio parameter. If insertion is attempted on a fully
        connected network or deletion is attempted on a network with no
        connections, the mutation process starts over.

     Constructor takes a dictionary with the following parameter fields:
       length
       initLowerLimit, initUpperLimit
       lowerCap, upperCap
       mutExploration
       mutInsDelRatio

     Optional fields:
       mutationAmplitude (default 1)
       initProbabilityOfConnection (default 1) -
         provides a mechanism for generating sparse networks.
	'''
	def __init__(self, params):
		super(Individual, self).__init__(params)

		self.setParamDefault('mutationAmplitude', 1.0)
		self._ensureParamIntegerness('mutationAmplitude')

		self._ensureParamIntegerness('initLowerLimit')
		self._ensureParamIntegerness('initUpperLimit')

		if self.paramExists('lowerCap'):
			self._ensureParamIntegerness('lowerCap')
		else:
			self.setParamDefault('lowerCap', -1.*np.inf)
		if self.paramExists('upperCap'):
			self._ensureParamIntegerness('upperCap')
		else:
			self.setParamDefault('upperCap', np.inf)

	def _ensureParamIntegerness(self, paramName):
		if not self.params[paramName].is_integer():
			raise ValueError(paramName + ' should be an integer (is ' + str(self.params[paramName]) + ')')

	def requiredParametersTranslator(self):
		t = super(Individual, self).requiredParametersTranslator()
		t['toFloat'].remove('relativeMutationAmplitude')
		t['toFloat'].update({'upperCap', 'lowerCap'})
		return t

	def optionalParametersTranslator(self):
		t = super(Individual, self).optionalParametersTranslator()
		t['toFloat'].difference_update({'upperCap', 'lowerCap'})
		t['toFloat'].add('mutationAmplitude')
		return t

	def isAZeroWeight(self, pos):
		# Redefining to safeguard against possible forgetful alterations of the parent class
		return self.values[pos] == 0.0

	def changeWeight(self, pos):
		inc = np.random.choice(inclusiveRange(-1.*self.params['mutationAmplitude'], self.params['mutationAmplitude']))
		self.values[pos] = np.clip(self.values[pos] + inc, self.params['lowerCap'], self.params['upperCap'])
#		print 'Increment by ' + str(inc) + ' has been attempted'

	def getAnInitialValue(self):
		return np.random.choice(inclusiveRange(self.params['initLowerLimit'], self.params['initUpperLimit']))

	def increment(self):
		if not np.isfinite(self.params['lowerCap']) or not np.isfinite(self.params['upperCap']):
			raise ValueError('Caps must be specified to use increment()')

#		print 'Incrementing ' + str(self)
		lcap = int(self.params['lowerCap'])
		ucap = int(self.params['upperCap'])
		base = ucap-lcap+1
#		print 'Bounds are ' + str(lcap) + ' and ' + str(ucap) + ', base is ' + str(base)

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
			numRepr += (int(val)-lcap)*(base**order)
			order += 1
#		print 'Current numerical representation is ' + str(numRepr)

		numRepr += 1

		if numRepr / (base**order) >= 1:
#			print 'Upper cap is hit!'
			self.setValuesToTheFirstSet()
			return False

		while order > 0:
			order -= 1
			curDig = numRepr / (base**order)
			numRepr -= curDig*(base**order)
#			print 'For order ' + str(order) + ' the digit is ' + str(curDig) + ': the remainder is ' + str(numRepr)
			self.values[order] = float(lcap + curDig)
#		print 'Ended up with ' + str(self)

		self.mask = map(lambda x: x!=0.0, self.values)

		return True

	def __str__(self):
		representation = str(self.id)
		for value in self.values:
			representation += ' '
			representation += str(int(value)) # default is too annoying
		return representation
