from abc import ABCMeta, abstractmethod
from itertools import izip

from tools.algorithms import sumOfDicts, listsIntersect

##### Abstract base class for grids #####

class Grid(object):
	'''Abstract base class for ordered sets of points in multidimensional spaces
     with labeled axes.
     It makes sure that all daughter classes are:
      * iterable
      * indexable
      * measurable by len()
      * can produce a full list of axes labels with paramNames() method
     Defines __repr__ and operators + and *.
	'''
	__metaclass__ = ABCMeta

	@abstractmethod
	def __len__(self):
		pass

	@abstractmethod
	def __iter__(self):
		pass

	@abstractmethod
	def __getitem__(self, i):
		'''Call super on this one for bounds checking'''
		if i >= len(self):
			raise IndexError('Grid index out of range')

	@abstractmethod
	def paramNames(self):
		pass

	def __repr__(self):
		listOfStrs = map(str, list(self))
		outStr = '[' + ',\n '.join(listOfStrs) + ']'
		return outStr

	def __str__(self):
		return str(list(self))

	def __add__(self, other):
		return SumOfGrids(self, other)

	def __mul__(self, other):
		if issubclass(type(other), Grid):
			return ProductOfGrids(self, other)
		elif type(other) is int:
			return ProductOfGridAndAnInteger(self, other)
		else:
			raise NotImplementedError

	def __rmul__(self, other):
		if type(other) is int:
			return ProductOfGridAndAnInteger(self, other)
		else:
			raise NotImplementedError

	def concatenate(self, other):
		return ConcatenationOfGrids(self, other)

##### Composite grid classes #####

class ProductOfGrids(Grid):
	'''Cartesian product of two grids'''
	def __init__(self, first, second):
		if listsIntersect(first.paramNames(), second.paramNames()):
			raise ValueError('Intersecting parameter name sets are not allowed for Grids in Cartesian products:\n'
												'The sets were as follows: ' + str(first.paramNames()) + ', ' + str(second.paramNames()))
		self.first = first
		self.second = second

	def __len__(self):
		return len(self.first)*len(self.second)

	def __iter__(self):
		for firstPoint in self.first:
			for secondPoint in self.second:
				yield sumOfDicts(firstPoint, secondPoint)

	def __getitem__(self, i):
		super(ProductOfGrids, self).__getitem__(i)
		firstPoint = self.first[i / len(self.second)]
		secondPoint = self.second[i % len(self.second)]
		return sumOfDicts(firstPoint, secondPoint)

	def paramNames(self):
		return self.first.paramNames() + self.second.paramNames()

class SumOfGrids(Grid):
	'''Elementwise concatenation of two grids of the same length'''
	def __init__(self, first, second):
		if listsIntersect(first.paramNames(), second.paramNames()):
			raise ValueError('Intersecting parameter name sets are not allowed for Grids in elementwise concatenations:\n'
												'The sets were as follows: ' + str(first.paramNames()) + ', ' + str(second.paramNames()))
		if len(first) != len(second):
			raise ValueError('Lenghts of Grids must be equal for Grids in elementwise concatenations:\n'
												'The lenghts were as follows: ' + str(len(first)) + ', ' + str(len(second)))
		self.first = first
		self.second = second

	def __len__(self):
		return len(self.first)

	def __iter__(self):
		for firstPoint, secondPoint in izip(self.first, self.second):
			yield sumOfDicts(firstPoint, secondPoint)

	def __getitem__(self, i):
		super(SumOfGrids, self).__getitem__(i)
		return sumOfDicts(self.first[i], self.second[i])

	def paramNames(self):
		return self.first.paramNames() + self.second.paramNames()

class ProductOfGridAndAnInteger(Grid):
	'''A grid which repeats each element of another grid several times'''
	def __init__(self, grid, multiplier):
		self.baseGrid = grid
		self.multiplier = multiplier

	def __len__(self):
		return self.multiplier*len(self.baseGrid)

	def __iter__(self):
		for point in self.baseGrid:
			for _ in range(self.multiplier):
				yield point

	def __getitem__(self, i):
		super(ProductOfGridAndAnInteger, self).__getitem__(i)
		return self.baseGrid[i/self.multiplier]

	def paramNames(self):
		return self.baseGrid.paramNames()

class ConcatenationOfGrids(Grid):
	'''A concatenation of two grids with identical paramNames'''
	def __init__(self, first, second):
		if not set(first.paramNames()) == set(second.paramNames()):
			raise ValueError('Parameter name sets must coincide for grid concatenation.\n'
												'The sets were as follows: ' + str(first.paramNames()) + ', ' + str(second.paramNames()))
		self.first = first
		self.lenFirst = len(first)
		self.second = second
		self.lenSecond = len(second)

	def __len__(self):
		return self.lenFirst + self.lenSecond

	def __iter__(self):
		for point in self.first:
			yield point
		for point in self.second:
			yield point

	def __getitem__(self, i):
		super(ConcatenationOfGrids, self).__getitem__(i)
		if i<self.lenFirst:
			return self.first[i]
		else:
			return self.second[i-self.lenFirst]

	def paramNames(self):
		return self.first.paramNames()

##### Practical elementary grid classes #####

class Grid1d(Grid):
	'''Ordered set of points in one-dimensional space with a label on the axis'''
	def __init__(self, paramName, paramVals):
		self.name = paramName
		self.vals = paramVals

	def __len__(self):
		return len(self.vals)

	def __iter__(self):
		for val in self.vals:
			yield {self.name: val}

	def __getitem__(self, i):
		super(Grid1d, self).__getitem__(i)
		return {self.name: self.vals[i]}

	def paramNames(self):
		return [self.name]

class LinGrid(Grid1d):
	'''Ordered set of uniformly spaced points in one-dimensional numeric space'''
	def __init__(self, paramName, baseValue, increment, downSteps, upSteps):
		getVal = lambda i: float(baseValue + float(i)*increment)
		vals = [getVal(i) for i in xrange(-1*downSteps, upSteps+1)]
		super(LinGrid, self).__init__(paramName, vals)

class LogGrid(Grid1d):
	'''Ordered set of log spaced points in one-dimensional numeric space'''
	def __init__(self, paramName, baseValue, multiplier, downSteps, upSteps):
		getVal = lambda i: float(baseValue * (multiplier**i))
		vals = [getVal(i) for i in xrange(-1*downSteps, upSteps+1)]
		super(LogGrid, self).__init__(paramName, vals)

class TrivialGrid(Grid1d):
	'''Ordered set of points in 1d space consisting of one point repeated
     N times
	'''
	def __init__(self, paramName, paramVal, size):
		super(TrivialGrid, self).__init__(paramName, [paramVal]*size)

class Grid1dFromFile(Grid1d):
	'''Ordered set of points in 1d space with values read from a file'''
	def __init__(self, paramName, valuesFileName, size=None, applyFunction=None):
		with open(valuesFileName, 'r') as valuesFile:
			valuesStr = valuesFile.read()
		vstrs = valuesStr.split()
		if size:
			if len(vstrs) < size:
				raise ValueError('Grid in the file is too small: ' +
													str(size) + 'values requested, ' +
													str(len(vstrs)) + ' available at ' + valuesFileName)
			vstrs = vstrs[:size]
		if applyFunction:
			vstrs = map(applyFunction, vstrs)
		super(Grid1dFromFile, self).__init__(paramName, vstrs)
