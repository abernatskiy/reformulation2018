import numpy as np
from realVectorTunableBoundsSureMutation import Individual as RealVectorTunableBoundsSureMutation

class Individual(RealVectorTunableBoundsSureMutation):
	'''Class for evolutionary individuals described by a vector of
     real-valued weights taken from [initLowerLimit, initUpperLimit]
     of constant length, with a single-valued score represented
     by a real number.

     Unlile realVectorTunableBoundsSureMutation, this class
     keeps track of which weights are close to zero and which
     are not. Whether the weight is close to zero or not is
     determined by a reloadable member function isAZeroWeight(self, pos).
     The mutation proceeds as follows:
      - with probability of mutExploration, the mutation operator
        will attempt to change a randomly picked nonzero weight
        using the reloadable changeWeight(self, pos) function.
        If the result ends up being close to zero, the connection
        will be removed;
      - all other cases are divided between the insertions and
        deletions. Ratio of the frequencies is controlled by the
        mutInsDelRatio parameter.
     Constructor takes a dictionary with the following parameter
     fields:
       length
       initLowerLimit, initUpperLimit
       mutExploration
       relativeMutationAmplitude
       mutInsDelRatio
     Optional fields:
       initProbabilityOfConnection (default 1) -
         provides a mechanism for generating sparse networks.
       lowerCap, upperCap (default -Inf, Inf)
	'''
	def __init__(self, params):
		super(Individual, self).__init__(params)

		if not self.params.has_key('initProbabilityOfConnection'):
			self.params['initProbabilityOfConnection'] = 1.0

		self.changeFrac = self.params['mutExploration']
		self.deleteFrac = (1.0 - self.changeFrac)/(self.params['mutInsDelRatio']+1)
		self.insertFrac = 1.0 - self.changeFrac - self.deleteFrac

		self.mask = map(lambda x: x<self.params['initProbabilityOfConnection'], np.random.random(self.params['length']))

		for pos,connExists in enumerate(self.mask):
			if not connExists:
				self.values[pos] = 0.0

	def requiredParametersTranslator(self):
		t = super(Individual, self).requiredParametersTranslator()
		t['toFloat'].update({'mutExploration', 'mutInsDelRatio'})
		return t

	def optionalParametersTranslator(self):
		t = super(Individual, self).optionalParametersTranslator()
		t['toFloat'].add('initProbabilityOfConnection')
		return t

	def _getRandomPosition(self, boolConnType):
		positions = []
		for pos,connExists in enumerate(self.mask):
			if connExists == boolConnType:
				positions.append(pos)
		if positions == []:
			return -1
		else:
			return np.random.choice(positions)

	def isAZeroWeight(self, pos):
		return self.values[pos] == 0.0

	def _insert(self):
#		print 'Inserting'
		insPos = self._getRandomPosition(False)
#		print 'Got position ' + str(insPos)
		if insPos != -1:
			self.values[insPos] = self.getAnInitialValue()
#			print 'Initialized a weight with ' + str(self.values[insPos])
			if not self.isAZeroWeight(insPos):
#				print 'Nontrivial change - returning True'
				self.mask[insPos] = True
				return True
			else:
#				print 'Trivial change - returning False'
				self.values[insPos] = 0.0
		return False

	def _delete(self):
		delPos = self._getRandomPosition(True)
		if delPos != -1:
			self.mask[delPos] = False
			self.values[delPos] = 0.0
			return True
		return False

	def _change(self):
		mutPos = self._getRandomPosition(True)
		if mutPos != -1:
			oldVal = self.values[mutPos]
			self.changeWeight(mutPos)
			if self.isAZeroWeight(mutPos):
				self.values[mutPos] = 0.0
				self.mask[mutPos] = False
			if oldVal != self.values[mutPos]:
				return True
		return False

	def mutate(self):
		mutated = False
#		print 'Mutating ' + str(self)
		while not mutated:
			randVal = np.random.random()
			if randVal < self.changeFrac:
#				print 'Chose change'
				mutated = self._change()
			elif randVal < (self.changeFrac + self.insertFrac):
#				print 'Chose insertion'
				mutated = self._insert()
			else:
#				print 'Chose deletion'
				mutated = self._delete()
		self.renewID()
#		print 'Result is ' + str(self)
		return True

	def setValuesToTheFirstSet(self):
		super(Individual, self).setValuesToTheFirstSet()
		self.mask = map(lambda x: x != 0.0, self.values)
