#!/usr/bin/python2

import numpy as np
import matplotlib.pyplot as plt
import os
import fnmatch

def plotFitnessTS(filename, plotColor, plotStd=True):
	fitnessTS = np.loadtxt(filename)
	fitnessMeanTS = np.mean(fitnessTS, axis=0)
	fitnessStdTS = np.std(fitnessTS, axis=1)*1.96/np.sqrt(float(fitnessTS.shape[1]))

	fitnessLower = fitnessMeanTS - fitnessStdTS
	fitnessUpper = fitnessMeanTS + fitnessStdTS

	gens = np.arange(0,len(fitnessMeanTS))

	plt.xlabel('Generations')
	plt.ylabel('Fitness')

	if plotStd:
		plt.plot(gens, fitnessLower, gens, fitnessUpper, color=plotColor, alpha=0.5)
		plt.fill_between(gens, fitnessLower, fitnessUpper, where=fitnessUpper>=fitnessLower, facecolor=plotColor, alpha=0.3, interpolate=True)
	plt.plot(gens, fitnessMeanTS, color=plotColor, label=filename)

def plotFitnessTSFromList(fitnessTS, plotColor, plotStd=True, label=None):
	fitnessMeanTS = np.mean(fitnessTS, axis=1)
	fitnessStdTS = np.std(fitnessTS, axis=1)*1.96/np.sqrt(float(fitnessTS.shape[1]))

	fitnessLower = fitnessMeanTS - fitnessStdTS
	fitnessUpper = fitnessMeanTS + fitnessStdTS

	gens = np.arange(0,len(fitnessMeanTS))

	plt.xlabel('Generations')
	plt.ylabel('Fitness')

	if plotStd:
		plt.plot(gens, fitnessLower, gens, fitnessUpper, color=plotColor, alpha=0.5)
		plt.fill_between(gens, fitnessLower, fitnessUpper, where=fitnessUpper>=fitnessLower, facecolor=plotColor, alpha=0.3, interpolate=True)
	plt.plot(gens, fitnessMeanTS, color=plotColor, label=label)

if __name__ == '__main__':
	#plotFitnessTS('fg16.0sg4.0cc0.0_fitnessTimeSeries.dat', 'red')

	colors = ['red', 'yellow', 'green', 'cyan', 'blue', 'violet']
	colorIdx = 0

	for file in os.listdir('.'):
		if fnmatch.fnmatch(file, 'fg16.0sg*cc*_fitnessTimeSeries.dat'):
			plotFitnessTS(file, colors[colorIdx], plotStd=False)
	#		plotFitnessTS(file, colors[colorIdx])
			colorIdx = (colorIdx + 1) % 6

	plt.legend(loc=4)
	plt.show()
