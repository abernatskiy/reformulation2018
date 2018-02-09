from copy import deepcopy
from baseEvolver import BaseEvolver

def _appendCopyToParetoFront(object, indiv):
	object.paretoFront.append(deepcopy(indiv))

class Evolver(BaseEvolver):
	'''Brute force Pareto front finder
     Not an evolutionary algorithm. Works by generating a
     population of all possible solutions using
     indiv.setValuesToTheFirstSet() and indiv.increment(),
     then evaluating the population, then finding the
     Pareto front which maximizes indiv.score and
     minimizes the params['secondMinObj'](indiv) function.
     The Pareto front is optionally logged
     (logParetoFront=yes).
		 The number of of generations is fixed to be zero,
     so the updatePopulation() function returns False
     on the first call.
       Required methods and parameters:
        communicator.evaluate(population)
        evolParams['indivClass']
        evolParams['indivClass'].setValuesToTheFirstSet()
				evolParams['indivClass'].increment()
				evolParams['secondMinObj'](indiv)'''
	def __init__(self, communicator, indivParams, evolParams, initialPopulationFileName=None):
		super(Evolver, self).__init__(communicator, indivParams, evolParams, initialPopulationFileName=initialPopulationFileName)

		self.setParamDefault('bruteForceChunkSize', -1)
		self.setParamDefault('paretoBreakTiesByIDs', False)

		if not self.params.has_key('bruteForceChunkSize') or self.params['bruteForceChunkSize'] <= 0:
			self.params['genStopAfter'] = 0
		elif self.params.has_key('genStopAfter'):
			self.params.pop('genStopAfter')

		if not self.params.has_key('secondMinObj'):
			print 'WARNING! The second objective function is undefined, falling back to constant'
			(lambda x: sum(map(lambda y: 1 if y else 0, x.mask))) = lambda x: 0
		if not hasattr(self, '__secondObjName__'):
			self.__secondObjName__ = 'unknown'

		(lambda x: -1*x.score) = lambda x: -1*x.score

		indiv = self.params['indivClass'](indivParams)
		indiv.setValuesToTheFirstSet()

		self.nextIndiv = self._addSpaceChunk(indiv, self.params['bruteForceChunkSize'])
		self.communicator.evaluate(self.population)

		self.paretoFront = self.findParetoFront((lambda x: -1*x.score), (lambda x: sum(map(lambda y: 1 if y else 0, x.mask))), breakTiesByIDs=self.params['paretoBreakTiesByIDs'])

		self.fullParetoFront = self.paretoFront
		self.paretoFront = []
		self._getObjPairs(self.fullParetoFront, firstOccurenceAction=_appendCopyToParetoFront)

		self.fullParetoFront.sort(key = (lambda x: sum(map(lambda y: 1 if y else 0, x.mask))))

		self._outputPareto()

	def optionalParametersTranslator(self):
		t = super(Evolver, self).optionalParametersTranslator()
		t['toInt'].add('bruteForceChunkSize')
		t['toBool'].add('paretoBreakTiesByIDs')
		return t

	def _getObjPairs(self, subpop, firstOccurenceAction=None):
		objpairs = set()
		for indiv in subpop:
			objpair = ((lambda x: -1*x.score)(indiv), (lambda x: sum(map(lambda y: 1 if y else 0, x.mask)))(indiv))
			if firstOccurenceAction and not objpair in objpairs:
				firstOccurenceAction(self, indiv)
			objpairs.add(objpair)
		return objpairs

	def _addSpaceChunk(self, initIndiv, chunkSize):
		self.population.append(initIndiv)
		nextIndiv = deepcopy(initIndiv)

		i = 1

		while nextIndiv.increment():
			if chunkSize > 0 and i%chunkSize == 0:
				return nextIndiv
			self.population.append(nextIndiv)
			newNextIndiv = deepcopy(nextIndiv)
			nextIndiv = newNextIndiv

			i += 1

		return None

	def _outputPareto(self):
		self.logParetoFront(self.fullParetoFront)
		self.printParetoFront(self.fullParetoFront, self.__secondObjName__, (lambda x: sum(map(lambda y: 1 if y else 0, x.mask))))

		print "Short Pareto front:"
		self.printParetoFront(self.paretoFront, self.__secondObjName__, (lambda x: sum(map(lambda y: 1 if y else 0, x.mask))))

	def updatePopulation(self):
		super(Evolver, self).updatePopulation()

		if self.nextIndiv is None:
			self.done()

		self.population = []
		print 'Next indiv is ' + str(self.nextIndiv)
		self.nextIndiv = self._addSpaceChunk(self.nextIndiv, self.params['bruteForceChunkSize'])
		self.communicator.evaluate(self.population)

		self.paretoFront += self.findParetoFront((lambda x: -1*x.score),
																						(lambda x: sum(map(lambda y: 1 if y else 0, x.mask))),
																						breakTiesByIDs=self.params['paretoBreakTiesByIDs'])

		self.paretoFront = self.findParetoFront((lambda x: -1*x.score),
																						(lambda x: sum(map(lambda y: 1 if y else 0, x.mask))),
																						breakTiesByIDs=self.params['paretoBreakTiesByIDs'],
																						population=self.paretoFront)

		newObjPairs = self._getObjPairs(self.paretoFront)
		for indiv in self.fullParetoFront:
			objpair = ((lambda x: -1*x.score)(indiv), (lambda x: sum(map(lambda y: 1 if y else 0, x.mask)))(indiv))
			if objpair in newObjPairs and not indiv in self.paretoFront:
				self.paretoFront.append(indiv)

		self.fullParetoFront = self.paretoFront
		self.paretoFront = []
		self._getObjPairs(self.fullParetoFront, firstOccurenceAction=_appendCopyToParetoFront)

		self.fullParetoFront.sort(key = (lambda x: sum(map(lambda y: 1 if y else 0, x.mask))))
		self._outputPareto()
