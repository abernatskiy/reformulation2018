import numpy as np
from trinaryVector import Individual as TriVecIndividual

class Individual(TriVecIndividual):
	'''Class for evolutionary individuals described by a vector of 
     numbers taken from {-1,0,1} of constant length, with advanced 
     mutation operatot. Constructor takes a dictionary with the 
     following parameter fields:
       length              - length of the vector
       mutExploration      - fraction of density-preserving mutations
       mutInsDelRatio      - ratio of inserting mutations to deletions
	'''
	def __init__(self, params):
		super(TriVecIndividual, self).__init__(params)
		self.changeFrac = self.params['mutExploration']
		self.deleteFrac = (1.0 - self.changeFrac)/(self.params['mutInsDelRatio']+1)
		self.insertFrac = 1.0 - self.changeFrac - self.deleteFrac
		self.values = np.random.random_integers(-1, 1, size=self.params['length'])

	def requiredParametersTranslator(self):
		t = super(Individual, self).requiredParametersTranslator()
		t['toFloat'].update({'mutExploration', 'mutInsDelRatio'})
		return t

	def insert(self):
		space = len(self.values) - np.count_nonzero(self.values)
		if space < 1:
			return False
		pos = np.random.randint(space)
		for i in xrange(len(self.values)):
			if self.values[i] == 0:
				if pos == 0:
					self.values[i] = 1 if np.random.random() > 0.5 else -1
					return True
				else:
					pos -= 1
		print("Insert: One should not dwell here\n")

	def delete(self):
		space = np.count_nonzero(self.values)
		if space < 1:	
			return False
		pos = np.random.randint(space)
		for i in xrange(len(self.values)):
			if self.values[i] != 0:
				if pos == 0:
					self.values[i] = 0
					return True
				else:
					pos -= 1
		print("Delete: One should not dwell here\n")

	def change(self):
		space = np.count_nonzero(self.values)
		if space < 1:
			return False
		pos = np.random.randint(space)
		for i in xrange(len(self.values)):
			if self.values[i] != 0:
				if pos == 0:
					self.values[i] = 1 if self.values[i] == -1 else -1
					return True
				else:
					pos -= 1
		print("Change: One should not dwell here\n")

	def mutate(self):
		mutated = False
		while not mutated:
			randVal = np.random.random()
			if randVal < self.changeFrac:
				mutated = self.change()
			elif randVal < (self.changeFrac + self.insertFrac):
				mutated = self.insert()
			else:
				mutated = self.delete()
		if mutated:
			self.renewID()
		return mutated
