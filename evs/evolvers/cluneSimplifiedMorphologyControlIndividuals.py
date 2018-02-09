import numpy as np
from copy import deepcopy
from cluneSimplified import Evolver as CluneSimplified

class Evolver(CluneSimplified):
	'''Same as cluneSimplified, but expects the Individual class to be a
     composite of a class decribing agent's morphology and controller.
     Given an Individual object i, those are expected to reside at i.parts[0]
     and i.parts[1], correspondingly. The connection cost is computed based
     on just the conteroller; also, if initialPopulationType=sparse, only the
     controllers are made to be sparse in the initial population. Otherwise,
     the behavior is identical to cluneSimplified. Below is a copy of its
     docstring.


     Multiobjective algorithm which minimizes the connection cost alongside
     with maximizing the fitness function. It is similar to the technique used
     in the 2013 Clune Mouret Lipson "The evolutionary origins of modularity"
     paper; the difference is that instead of using NSGA-II, we simply keep the
     whole Pareto front at each generation and add its offsprings to the
     population until it restores its size.

     Required parameters:
       evolParams['populationSize']
       evolParams['initialPopulationType'] - can be 'random' or 'sparse'.
         If 'sparse' is chosen, the initial population will be composed of
         individulas with all genes set to zero and mutated once. To do so,
         the algorithm will use the following method of the individual class:
           evolParams['indivClass'].setValuesToZero().
         Feel free to use it to redefine the meaning of the sparsity!
         More info on benefits of sparse initial populations can be found in
         2015 Bernatskiy Bongard "Exploiting the relationship between structural
         modularity and sparsity for faster network evolution".

     Optional parameters:
       evolParams['secondObjectiveProbability'] - if provided, connection cost
         will only be taken into account with the specified probability. If it
         is not taken into account, the algorithm will assume that the
         individual with larger fitness dominates regardless of connection cost.
         See 2013 Clune et al.
       evolParams['useMaskForSparsity'] - use mask instead of comparing the
         fields to zero to count nonzero values.
       evolParams['noiseAmplitude'] - if provided, noisy evaluations with a
			  uniformly distributed noise of given amplitude will be simulated.

     NOTE: Individual classes with surefire mutation operator are OK.'''

	def getSparseIndividual(self):
		indiv = self.params['indivClass'](self.indivParams)
		indiv.parts[1].setValuesToZero()
		indiv.parts[1].mutate()
		return indiv

	def getConnectionCostFunc(self):
		connectionCostFunc = lambda x: len(filter(lambda y: y!=0, x.parts[1].values))
		self.secondObjectiveLabel = 'connection cost of the controller'
		return connectionCostFunc
