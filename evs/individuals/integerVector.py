import numpy as np
from baseIndividual import BaseIndividual

class Individual(BaseIndividual):
	'''Base class for integer-valued vectors. Do not use, inherit.

     Note: for Individuals which are specialized to represent
     integer network weights see the integerWeight* family of
     Individual classes. Due to the similarity in mutation
     mechanisms those classes inherit from realVector and
     represent the weights as real values internally.
  '''
	def fromStr(self, representation):
		vals = map(int, representation.split())
		self.id = vals[0]
		self.values = vals[1:]

	def setValuesToZero(self): # for sparse-first search only! Use setValuesToTheFirstSet() for bruteforce applications
		self.values = np.zeros(self.params['length'], dtype=np.int)
		self.renewID()

	def requiredParametersTranslator(self):
		t = super(Individual, self).requiredParametersTranslator()
		t['toInt'].add('length')
		return t
