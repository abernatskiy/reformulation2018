import re
import importlib
import numpy as np

from baseIndividual import BaseIndividual

class Individual(BaseIndividual):
	'''Class for evolutionary individuals glued together from individuals of other
	   classes. Mutation of such composite individual mutates only one of its
	   parts; each class in the composite is chosen randomly with some fixed
	   probability assigned to it.

	   Constructor takes a dictionary with the following parameter fields:

	     compositeClass0, probabilityOfMutatingClass0
	     compositeClass1, probabilityOfMutatingClass1
	     ...
	     compositeClassN, probabilityOfMutatingClassN
	     - names and probabilities of part classes

	     <partClassParameterName>Class?
	     - params passed through the constructor of the composite to the
	     constructors of part classes, after stripping the trailing "Class?"

	   For string representations, the class assumes that each of the part has a
	   representation of form "ID GEN". The representations are then combined as
	   follows:
	     "ID0 GEN0" "ID1 GEN1" ... "IDN GENN" ->
	     -> "CommonID GEN0 GEN1 ... GENN"
	'''
	def __init__(self, params):
		super(Individual, self).__init__(params)
		self._extractPartClasses()
		self._extractClassParameters()
		self._extractMutationProbabilities()
		self.parts = [ self.partClasses[i](self.classParams[i]) for i in range(self.numClasses) ]

	def _extractPartClasses(self):
		# Extracting partClasses and numClasses
		partClassesNames = {}
		classPattern = re.compile('^compositeClass[0-9]+$')
		numPattern = re.compile('[0-9]+$')
		for pn, pv in self.params.iteritems():
			if classPattern.match(pn):
				classNum = int(numPattern.search(pn).group())
				partClassesNames[classNum] = pv
		# Determining the number of classes
		self.numClasses = len(partClassesNames)
		# Checking if numbers are sequential
		if partClassesNames.keys() != list(range(self.numClasses)):
			raise ValueError('Classes must be numbered sequentially starting from zero in the config, and they are not. Exiting.')
		# Loading the sources for all classes
		self.partClasses = []
		for i in range(len(partClassesNames)):
			self.partClasses.append(importlib.import_module('individuals.' + partClassesNames[i]).Individual)

	def _extractMutationProbabilities(self):
		mutProbDict = {}
		probPattern = re.compile('^probabilityOfMutatingClass[0-9]+$')
		numPattern = re.compile('[0-9]+$')
		for pn, pv in self.params.iteritems():
			if probPattern.match(pn):
				classNum = int(numPattern.search(pn).group())
				mutProbDict[classNum] = pv
		if mutProbDict.keys() != list(range(self.numClasses - 1)):
			raise ValueError('N-1 mutation probability must be provided for a composite of N Individual classes. Exiting.')
		self.mutationProbabilities = []
		for i in range(self.numClasses - 1):
			self.mutationProbabilities.append(mutProbDict[i])
		self.mutationProbabilities.append(1. - sum(self.mutationProbabilities))

	def _extractClassParameters(self):
		self.classParams = [ {} for _ in range(self.numClasses) ]
		paramsPattern = re.compile('Class[0-9]+$')
		paramsPatternFull = re.compile('^.*Class[0-9]+$')
		classPattern = re.compile('^compositeClass[0-9]+$')
		probPattern = re.compile('^probabilityOfMutatingClass[0-9]+$')
		numPattern = re.compile('[0-9]+$')
		for pn, pv in self.params.iteritems():
			if paramsPatternFull.match(pn) and not classPattern.match(pn) and not probPattern.match(pn):
				classNum = int(numPattern.search(pn).group())
				if classNum<0 or classNum>=self.numClasses:
					raise ValueError('I was given parameters for too many classes for this composite Individual. Exiting.')
				paramName = paramsPattern.split(pn)[0]
				self.classParams[classNum][paramName] = pv

	def requiredParametersTranslator(self):
		t = super(Individual, self).requiredParametersTranslator()
		t['toString'].add('^compositeClass[0-9]+$')
		return t

	def optionalParametersTranslator(self):
		t = super(Individual, self).optionalParametersTranslator()
		t['toFloat'].add('^probabilityOfMutatingClass[0-9]+$')
		return t

	def __str__(self):
		return str(self.id) + ' ' + ' '.join([ s.split(' ', 1)[1] for s in map(str, self.parts)])

	def mutate(self):
		roll = np.random.random()
		psum = 0.
		i = 0
		while psum < roll:
			psum += self.mutationProbabilities[i]
			i += 1
		i -= 1
		mutated = self.parts[i].mutate()
		if mutated:
			self.renewID()
		return mutated
