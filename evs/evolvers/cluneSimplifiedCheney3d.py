import __builtin__

from cluneSimplified import Evolver as CluneSimplifiedEvolver

class Evolver(CluneSimplifiedEvolver):
	'''Three-dimensional dragon, first of its kind'''
#	def __init__(self, communicator, indivParams, evolParams, initialPopulationFileName = None):
#		super(Evolver, self).__init__(communicator, indivParams, evolParams, initialPopulationFileName=initialPopulationFileName)

	def getMorphologicalAge(self):
		return lambda x: __builtin__.globalGenerationCounter - x.timeOfLastMorphologicalMutation

	def getMinimizableFuncs(self):
		return ([ self.getErrorFunc(), self.getConnectionCostFunc(), self.getMorphologicalAge() ], ['error', 'connection cost', 'morphological age'])

	def getCluneParetoFront(self):
		funcs, _ = self.getMinimizableFuncs()
		return self.findParetoFrontManyObjectives(funcs)

	def doParetoOutput(self, paretoFront):
		funcs, labels = self.getMinimizableFuncs()
		self.printParetoFrontMultipleObjectives(paretoFront, funcs, labels)
		self.logParetoFront(paretoFront)
		self.paretoWarning(paretoFront)
