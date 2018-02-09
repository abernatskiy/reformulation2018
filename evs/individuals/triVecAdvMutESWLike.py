import numpy as np
from trinaryVector import Individual as TriVecIndividual

class Individual(TriVecIndividual):
	'''Class for evolutionary individuals described by a vector of numbers taken
	   from {-1,0,1} of constant length with mutation operator taken from the
	   Espinosa-Soto Wagner 2010 paper (DOI: 10.1371/journal.pcbi.1000719).
	   Additionally, a function initSparse(self) is provided, which makes an empty
	   random vector and adds self.params['initDensity'] connections to it at
	   random. Constructor takes a dictionary with the following parameter fields:
       length              - length of the vector
       mutProbability      - probability of mutation per each E-S W gene (number
	                            of nodes is a square root of length)
       mutExploration      - fraction of connectivity-preserving mutations
       mutInsDelRatio      - ratio of insertion frequency to deletion frequency
	     initDensity         - number of connections the individual will have
	                           after a call to initSparse() method. If you don't
	                           use this functionality, parameters is not needed
	'''
	def __init__(self, params):
		super(TriVecIndividual, self).__init__(params)
		if not np.sqrt(self.params['length']).is_integer():
			raise ValueError('Length of such vectors should be a square of an integer')
		self.numNodes = int(np.sqrt(self.params['length']))
		self.changeFrac = self.params['mutExploration']
		self.deleteFrac = (1.0 - self.changeFrac)/(self.params['mutInsDelRatio']+1)
		self.insertFrac = 1.0 - self.changeFrac - self.deleteFrac
		self.values = np.random.random_integers(-1, 1, size=self.params['length'])

	def requiredParametersTranslator(self):
		t = super(Individual, self).requiredParametersTranslator()
		t['toFloat'].update({'mutExploration', 'mutInsDelRatio', 'mutProbability'})
		return t

	def optionalParametersTranslator(self):
		t = super(Individual, self).requiredParametersTranslator()
		t['toInt'].add('initDensity')
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

	def initSparse(self):
		self.values = np.zeros(self.params['length'])
		while np.count_nonzero(self.values) < self.params['initDensity']:
			self.insert()
		self.renewID()

	def countRegulators(self, node):
		adjMat = self.values.reshape(self.numNodes, self.numNodes)
		connections = adjMat[:, node]
		return np.count_nonzero(connections)

	def mutateNode(self, node):
		regulators = self.countRegulators(node)
		randNum = np.random.random()
		if randNum < self.deleteFrac and regulators != 0:
			# remove randomly selected regulator
			pos = np.random.randint(regulators)
			secondNode = 0
			while True:
				if self.values[secondNode*self.numNodes + node] != 0:
					if pos == 0:
						break
					pos -= 1
				secondNode += 1
			self.values[secondNode*self.numNodes + node] = 0
		elif randNum < (self.deleteFrac + self.insertFrac) and regulators != self.numNodes:
			# add randomly selected regulator
			pos = np.random.randint(self.numNodes - regulators)
			secondNode = 0
			while True:
				if self.values[secondNode*self.numNodes + node] == 0:
					if pos == 0:
						break
					pos -= 1
				secondNode += 1
			self.values[secondNode*self.numNodes + node] = -1 if np.random.random() < 0.5 else 1
		else:
			if regulators != 0:
				# remove randomly selected regulator
				pos = np.random.randint(regulators)
				secondNode = 0
				while True:
					if self.values[secondNode*self.numNodes + node] != 0:
						if pos == 0:
							break
						pos -= 1
					secondNode += 1
				self.values[secondNode*self.numNodes + node] = 0
				regulators -= 1

			# add randomly selected regulator
			pos = np.random.randint(self.numNodes - regulators)
			secondNode = 0
			while True:
				if self.values[secondNode*self.numNodes + node] == 0:
					if pos == 0:
						break
					pos -= 1
				secondNode += 1
			self.values[secondNode*self.numNodes + node] = -1 if np.random.random() < 0.5 else 1

	def mutate(self):
		mutated = False
		for i in xrange(self.numNodes):
			if np.random.random() < self.params['mutProbability']:
				self.mutateNode(i)
				mutated = True
#		if mutated:
		self.renewID()
		return mutated
