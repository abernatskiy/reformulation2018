import os
import time
from baseCommunicator import BaseCommunicator

class Communicator(BaseCommunicator):
	'''Communicator which uses text files for 
     data exchange between a server and a client.'''
	def __init__(self, fninput='evaluations.txt', fnoutput='individuals.txt'):
		super(BaseCommunicator, self).__init__()
		self.fninput = fninput
		self.fnoutput = fnoutput

	def write(self, indivList):
		with open(self.fninput, 'w') as finput:
			finput.close()
		foutput = open(self.fnoutput, 'w') 
		for indiv in indivList:
			foutput.write(str(indiv) + '\n')
		foutput.close()

	def read(self):
		while os.path.getsize(self.fninput) == 0:
			time.sleep(0.05)
		evaluations = []
		finput = open(self.fninput, 'r')
		for line in finput:
			evaluations.append(line)
		finput.close()
		return evaluations
