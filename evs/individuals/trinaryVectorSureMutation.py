import numpy as np
from trinaryVector import Individual as TriVecIndividual

class Individual(TriVecIndividual):
	'''Class for evolutionary individuals described by a vector of 
     numbers taken from {-1,0,1} of constant length, with 
     a single-valued score represented by a FPN. Unlike 
     trinaryVector, mutation is sure for this one - it always
     changes the genome. Constructor takes a 
     dictionary with the following parameter fields
       length     - length of the vector
	'''
	def mutate(self):
		idx = np.random.randint(self.params['length'])
		possibleVals = [-1, 0, 1]
		possibleVals.remove(self.values[idx])
		self.values[idx] = np.random.choice(possibleVals)
		self.renewID()
		return True
