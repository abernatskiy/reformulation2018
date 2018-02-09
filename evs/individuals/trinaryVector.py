import numpy as np
from baseIndividual import BaseIndividual

class Individual(BaseIndividual):
	'''Class for evolutionary individuals described by a vector of 
     numbers taken from {-1,0,1} of constant length, with 
     a single-valued score represented by a FPN. Constructor takes a 
     dictionary with the following parameter fields
       length     - length of the vector
       mutationProbability - probability that mutation occurs upon 
                             mutate() call (for each value)
	'''
	def __init__(self, params):
		super(Individual, self).__init__(params)
		self.values = np.random.random_integers(-1, 1, size=self.params['length'])

	def fromStr(self, representation):
		integers = map(int, representation.split())
		self.id = integers[0]
		self.values = integers[1:]
		self.renewID()

	def mutate(self):
		newValues = []
		mutated = False
		for val in self.values:
			if np.random.random() <= self.params['mutationProbability']:
				newValues.append(np.random.random_integers(-1, 1))
				if val != newValues[-1]:
					mutated = True
			else:
				newValues.append(val)
		if mutated:
			self.renewID()
			self.values = np.array(newValues)
			return True
		else:
			return False

	def setValuesToTheFirstSet(self): # for bruteforce searches
		self.values = -1*np.ones(self.params['length'], dtype=np.int)
		self.renewID()

	def increment(self): # for bruteforce searches
		'''Increments the trinary vector as if it was a trinary number.
       Returns False whenever the first value (corresponding to the trinary 0) is passed'''
		numRepr = 0
		order = 0
		base = 3
		for val in self.values:
			numRepr += (val+1)*np.power(base, order)
			order += 1
		numRepr += 1
		if numRepr / np.power(base, order) >= 1:
			self.setValuesToTheFirstSet()
			self.renewID()
			return False
		while order > 0:
			order -= 1
			curDig = numRepr / np.power(base, order)
			numRepr -= curDig*np.power(base, order)
			self.values[order] = curDig - 1
		self.renewID()
		return True

	def setValuesToZero(self): # for sparse-first search
		self.values = np.zeros(self.params['length'], dtype=np.int)
		self.renewID()

	def requiredParametersTranslator(self):
		t = super(Individual, self).requiredParametersTranslator()
		t['toInt'].add('length')
		t['toFloat'].add('mutationProbability')
		return t
