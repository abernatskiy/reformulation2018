import numpy as np
from baseIndividual import BaseIndividual

class Individual(BaseIndividual):
	'''Base class for real-valued vectors. Do not use, inherit.'''
	def fromStr(self, representation):
		vals = map(float, representation.split())
		self.id = int(vals[0])
		self.values = vals[1:]

	def setValuesToZero(self): # for sparse-first search only! Use setValuesToTheFirstSet() for bruteforce applications
		self.values = np.zeros(self.params['length'], dtype=np.float)
		self.renewID()

	def requiredParametersTranslator(self):
		t = super(Individual, self).requiredParametersTranslator()
		t['toInt'].add('length')
		return t
