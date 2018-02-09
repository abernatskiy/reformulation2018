import numpy as np
from trinaryVector import Individual as TriVecIndividual

layerSizes = [8,4,4]

class Individual(TriVecIndividual):
	'''Class for evolutionary individuals described by a vector of
     numbers taken from {-1,0,1} of constant length, with
     a single-valued score represented by a FPN.
     Mutation occurs with a probability of 1/mi in each
     group of genes of size mi (groups loosely correspond to
     weight matrices of a layered ANN). Mutation replaces the
     value with one randomly chosen from {-1,0,1}.
     There is a nonzero
     probability that mutation will not change the weights,
     but it is neglected and ID is always updated.
       length     - length of the vector
	'''
	def mutate(self):
		curpos = 0
		for ls in layerSizes:
			for i in range(ls):
				if np.random.random() < 1./float(ls):
					self.values[curpos+i] = np.random.randint(-1,2)
			curpos += ls
		self.renewID()
		return True
