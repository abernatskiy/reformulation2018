#!/usr/bin/python2

# A script which takes rawData.ssv and spits out files with fields of values
# Values I need:
# mean fitness
# relative error (stddev/mean fitness)
# symmetricity
# no of connections

import numpy as np

class Network(object):
	def __init__(self, arr):
		self.weights = map(int, arr)
	def __eq__(self, other):
		return self.weights == other.weights
	def __repr__(self):
		return str(self)
	def __str__(self):
		return str(self.weights)
	def isSymmetrical(self):
		'Checks if vector of weights is invariant under reversal'
		return self.weights == self.weights[::-1]
	def nonZeroWeights(self):
		'How many real connections does it have?'
		return len(self.weights) - self.weights.count(0)
	def negativeWeights(self):
		'How many negative weights does it have?'
		return sum(1 for number in self.weights if number<0)
	def positiveNumbers(self):
		'How many negative weights does it have?'
		return sum(1 for number in self.weights if number>0)
	def isModular(self):
		'Modularity in a limited sense - true if no node has connections to more than one node. Works for 2x2 systems only.'
		return self.isSymmetrical() and self.nonZeroWeights() == 2

class Run(object):
	def __init__(self, arr):
		self.seed = int(arr[0].rstrip(':').lstrip('seed'))
		self.bestFitness = float(arr[1])
		self.id = int(arr[2])
		self.network = Network(arr[3:7])
	def __repr__(self):
		return str(self)
	def __str__(self):
		return 'Network ' + str(self.network) + ' with fitness ' + str(self.bestFitness) + ' (championed with seed ' + str(self.seed) + ')'

class Record(object):
	def __init__(self, strings):
		strings = line.split()
		self.forceGain = float(strings[1])
		self.sensorGain = float(strings[3])
		noOfRuns = (len(strings)-4)/7 # four fields for params data, seven fields per run
		self.runs = []
		for runNo in xrange(0, noOfRuns): 
			self.runs.append(Run(strings[4+7*runNo:11+7*runNo]))
	def __repr__(self):
		return str(self)
	def __str__(self):
		return 'forceGain: ' + str(self.forceGain) + ' sensorGain: ' + str(self.sensorGain) + ' noOfRuns: ' + str(len(self.runs))
	def avgFitness(self):
		fitnesses = np.array([ run.bestFitness for run in self.runs ])/self.sensorGain
		return fitnesses.mean()
	def relStdOfFitness(self):
		fitnesses = np.array([ run.bestFitness for run in self.runs ])
		return fitnesses.std()/fitnesses.mean()
	def avgNoOfConnections(self):
		connections = np.array([ float(run.network.nonZeroWeights()) for run in self.runs ])
		return connections.mean()
	def avgNoOfExitatoryConnections(self):
		exConnections = np.array([ float(run.network.positiveWeights()) for run in self.runs ])
		return exConnection.mean()
	def avgNoOfInhibitoryConnections(self):
		inConnections = np.array([ float(run.network.positiveWeights()) for run in self.runs ])
		return inConnections.mean()
	def symmetricity(self):
		symmetricityVec = np.array([ (1.0 if run.network.isSymmetrical() else 0.0) for run in self.runs ])
		return symmetricityVec.mean()
	def diversity(self):
		networksVec = [ tuple(run.network.weights) for run in self.runs ]
		networksSet = set(networksVec)
		return len(networksSet)
	def modularity(self):
		modularityVec = np.array([ (1.0 if run.network.isModular() else 0.0) for run in self.runs ])
		return modularityVec.mean()

records = []

file = open('rawResults.ssv', 'r')
for line in file:
	records.append(Record(line.split(' ')))
file.close()

def getField(funcName):
	global records
	return np.array([ [record.forceGain, record.sensorGain, getattr(record, funcName)()] for record in records ])

attributes = {'avgFitness', 'relStdOfFitness', 'avgNoOfConnections', 'avgNoOfExitatoryConnections', 'avgNoOfInhibitoryConnections', 'symmetricity', 'diversity', 'modularity' }

plotOptions = { 'avgFitness' 					: {'zscale' : 'log', 'zlabel' : 'Average fitness, s/m^2, log10 of' },
								'relStdOfFitness'			: {'zscale' : 'lin', 'zlabel' : 'Relative standard deviation of fitness' },
								'avgNoOfConnections'	: {'zscale' : 'lin', 'zlabel' : 'Average no of connections' },
								'symmetricity'				: {'zscale' : 'lin', 'zlabel' : 'Fraction of symmetrical networks' },
								'diversity'						: {'zscale' : 'lin', 'zlabel' : 'Number of unique evolved networks'},
								'modularity'					: {'zscale' : 'lin', 'zlabel' : 'Fraction of modular networks' } }

def plotField(funcName):
	global plotOptions
	import matplotlib.pyplot as plt
	field = getField(funcName)
	plt.xscale('log')
	plt.xlabel('forceGain, N')
	plt.yscale('log')
	plt.ylabel('sensorGain, m^2')
	if plotOptions[funcName]['zscale'] == 'log':
		plt.scatter(field[:,0], field[:,1], c=np.log10(field[:,2]), marker='s', s=110)
	else:
		plt.scatter(field[:,0], field[:,1], c=field[:,2], marker='s', s=110)
	plt.colorbar().set_label(plotOptions[funcName]['zlabel'])
	plt.savefig(funcName + '.png')
	plt.clf()

for funcName in plotOptions:
	plotField(funcName)
