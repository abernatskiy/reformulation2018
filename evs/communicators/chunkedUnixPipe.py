from unixPipe import Communicator as unixPipe

def chunks(l, n):
	'''Yield successive n-sized chunks from l.'''
	for i in xrange(0, len(l), n):
		yield l[i:i+n]

class Communicator(unixPipe):
	'''Communicator which uses unix pipes for 
     data exchange between a server and a client. 
     This one is adapted for longer inputs, which it 
     splits into 500-lines-long chunks.'''
	def evaluate(self, indivList):
		for chunk in chunks(indivList, 500):
			super(Communicator, self).evaluate(chunk)
