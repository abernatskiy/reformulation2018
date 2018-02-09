import numpy as np
from trinaryVector import Individual as TrinaryVectorIndividual

class Individual(TrinaryVectorIndividual):
	'''Trinary weights for a neural network with an elaborate three-way mutation operator.
     Required options:
       length
       mutExploration - given that the mutation occurs, its probability to flip a connection weight
       mutInsDelRatio - ratio of probabilities of mutation to insert a new connection or delete an old one
     Optional options:
       mutationProbability - probability that the mutation occurs at all, defaults to 1
  '''
	def __init__(self, params):
		super(Individual, self).__init__(params)

		if not self.params.has_key('mutationProbability'):
			self.params['mutationProbability'] = 1.

		self.modifyFrac = self.params['mutExploration']
		self.deleteFrac = (1.0 - self.modifyFrac)/(self.params['mutInsDelRatio']+1)
		self.insertFrac = 1.0 - self.modifyFrac - self.deleteFrac

	def requiredParametersTranslator(self):
		t = super(Individual, self).requiredParametersTranslator()
		t['toFloat'].remove('mutationProbability')
		t['toFloat'].add('mutExploration')
		t['toFloat'].add('mutInsDelRatio')
		return t

	def optionalParametersTranslator(self):
		t = super(Individual, self).optionalParametersTranslator()
		t['toFloat'].add('mutationProbability')
		return t

	def randomWeightPos(self, isAZeroWeight):
		positions = [ pos for pos,wt in enumerate(self.values) if (wt==0)==isAZeroWeight ]
		return None if positions == [] else np.random.choice(positions)

	def insertConnection(self):
		p = self.randomWeightPos(True)
		if p is None:
			return False
		else:
			self.values[p] = np.random.choice([-1,1])
			return True

	def deleteConnection(self):
		p = self.randomWeightPos(False)
		if p is None:
			return False
		else:
			self.values[p] = 0
			return True

	def modifyConnection(self):
		p = self.randomWeightPos(True)
		if p is None:
			return False
		else:
			self.values[p] = -1 if self.values[p] == 1 else 1
			return True

	def mutate(self):
		if np.random.random() > self.params['mutationProbability']:
			return False
		mutated = False
		while not mutated:
			r = np.random.random()
			if r < self.insertFrac:
				mutated = self.insertConnection()
			elif r < self.insertFrac + self.deleteFrac:
				mutated = self.deleteConnection()
			else:
				mutated = self.modifyConnection()
		self.renewID()
		return True
