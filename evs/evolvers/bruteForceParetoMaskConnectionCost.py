from bruteForcePareto import Evolver as BruteForcePareto

class Evolver(BruteForcePareto):
	'''Brute force Pareto front finder with a second
     objective of minimizing the number of True values at
     Individual.mask. See BruteForcePareto for details.'''
	def __init__(self, communicator, indivParams, evolParams, initialPopulationFileName=None):
		evolParams['secondMinObj'] = lambda x: sum(map(lambda y: 1 if y else 0, x.mask))
		self.__secondObjName__ = 'nonzero values'
		super(Evolver, self).__init__(communicator, indivParams, evolParams, initialPopulationFileName=initialPopulationFileName)
