#!/usr/bin/python2

import sys
if len(sys.argv) == 2:
	xlimit = int(sys.argv[1])
else:
	xlimit = 100

import numpy as np
import matplotlib.pyplot as plt
import os
import fnmatch

def plotFitnessTS(filename, plotColor, plotStd=True):
	global xlimit
	fitnessTS = np.loadtxt(filename)
#	print fitnessTS
	fitnessMeanTS = np.mean(fitnessTS, axis=1)
#	print fitnessMeanTS
	fitnessStdTS = np.std(fitnessTS, axis=1)*1.96/np.sqrt(float(fitnessTS.shape[1]))

	fitnessLower = fitnessMeanTS - fitnessStdTS
	fitnessUpper = fitnessMeanTS + fitnessStdTS

	gens = np.arange(0,len(fitnessMeanTS))

	plt.xlabel('Number of generations')

	if xlimit <= 30:
		plt.errorbar(gens, fitnessMeanTS, color=plotColor, yerr=fitnessStdTS, label=filename)
	else:
		if plotStd:
			plt.plot(gens, fitnessLower, gens, fitnessUpper, color=plotColor, alpha=0.5)
			plt.fill_between(gens, fitnessLower, fitnessUpper, where=fitnessUpper>=fitnessLower, facecolor=plotColor, alpha=0.3, interpolate=True)
		plt.plot(gens, fitnessMeanTS, color=plotColor, label=filename)

colors = ['black', 'red', 'yellow', 'green', 'cyan', 'blue', 'violet']
colorIdx = 0

print 'Plotting fitness...'

for file in os.listdir('.'):
	if fnmatch.fnmatch(file, '*.fitness'):
		plotFitnessTS(file, colors[colorIdx], plotStd=True)
		colorIdx = (colorIdx + 1) % 7
plt.ylabel('Fitness')
plt.legend(loc=4)
plt.title('Average fitness vs generation')
plt.xlim(0, xlimit)

#ax = plt.subplot(111)
#box = ax.get_position()
#ax.set_position([box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9])
#ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05))

plt.savefig('fitness.png', dpi=200)
plt.close()

print 'Plotting qvalue...'

for file in os.listdir('.'):
	if fnmatch.fnmatch(file, '*.qvalue'):
		plotFitnessTS(file, colors[colorIdx], plotStd=True)
		colorIdx = (colorIdx + 1) % 7
plt.ylabel('Q')
plt.legend(loc=4)
plt.title('Average Q vs generation')
plt.xlim(0, xlimit)

plt.savefig('qvalue.png', dpi=200)
plt.close()

print 'Plotting density...'

for file in os.listdir('.'):
	if fnmatch.fnmatch(file, '*.density'):
		plotFitnessTS(file, colors[colorIdx], plotStd=True)
		colorIdx = (colorIdx + 1) % 7
plt.ylabel('Number of connections')
plt.legend(loc=1)
plt.title('Average density vs generation')
plt.xlim(0, xlimit)

plt.savefig('density.png', dpi=200)
plt.close()
