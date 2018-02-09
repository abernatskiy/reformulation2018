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
		foutput = open(self.fnoutput, 'w') 
		for indiv in indivList:
			foutput.write(str(indiv) + '\n')
		foutput.close()

	def read(self):
		import sys
		sys.exit(0)
