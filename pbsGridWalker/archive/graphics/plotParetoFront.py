#!/usr/bin/python2

import numpy as np
import matplotlib
import argparse
import subprocess

pointSizeMultiplier = 16

def connectionCost(netDesc, genotypeBeginsAt):
	return sum([0.0 if x==0.0 else 1.0 for x in netDesc[(genotypeBeginsAt+1):]])

def rightLadder(x, y):
	N = len(x)
	if len(y) != N:
		raise ValueError('ladder() takes two arrays of equal size')
	xp = []
	yp = []
	for i in xrange(N-1):
		xp.append(x[i])
		yp.append(y[i])
		xp.append(x[i])
		yp.append(y[i+1])
	xp.append(x[N-1])
	yp.append(y[N-1])
	return xp, yp

class ParetoPlotter(object):
	def __init__(self, filename, fitnessPos=0, genotypeBeginsAt=1, secondObjFunc=lambda s: connectionCost(s, 1)):
		self.filename = filename
		self.paretoFront = {}
		with open(filename, 'r') as file:
			for line in file:
				self._parseLine(line, fitnessPos, genotypeBeginsAt, secondObjFunc)

	def _parseLine(self, line, fitnessPos, genotypeBeginsAt, secondObjFunc):
		if line[0] == '#' or line == '':
			return
		fvals = map(float, line.split())
		objpair = (fvals[fitnessPos], secondObjFunc(fvals))
		indiv = (int(fvals[genotypeBeginsAt]), fvals[(genotypeBeginsAt+1):])
		if not self.paretoFront.has_key(objpair):
			self.paretoFront[objpair] = []
		self.paretoFront[objpair].append(indiv)

	def __str__(self):
		return '{' + ',\n\n '.join(map(str, sorted(self.paretoFront.iteritems()))) + '}'

	def dataForPlot(self):
		global pointSizeMultiplier
		fit = []
		cc = []
		size = []
		for key in sorted(self.paretoFront.keys()):
			fit.append(-1.0*key[0])
			cc.append(key[1])
			size.append(pointSizeMultiplier*len(self.paretoFront[key]))
		return fit, cc, size

	def plot(self, colorPoints='r', colorLine='b', label='Pareto front', title=None, priority=0):
		self._plotData(colorPoints=colorPoints, colorLine=colorLine, label=label, priority=priority)
		self._plotAccessory(title=title)

	def _plotData(self, colorPoints='r', colorLine='b', label='Pareto front', priority=0, plotPoints=True):
		import matplotlib.pyplot as plt
		f,c,s = self.dataForPlot()
		fp, cp = rightLadder(f, c)
		plt.plot(fp, cp, color=colorLine, lw=3, zorder=priority*3+1, label=label)
		if plotPoints:
			plt.scatter(f, c, marker='o', c=colorPoints, s=s, lw=0, zorder=priority*3+2)

	def _plotAccessory(self, title=None, xlabel='-1.0*fitness', ylabel='connection cost', legend=True):
		import matplotlib.pyplot as plt
		plt.grid()
		plt.xlabel(xlabel)
		plt.ylabel(ylabel)
		if legend:
			plt.legend()
		if title:
			plt.title(title)
		else:
			plt.title('Pareto front from file ' + self.filename)

	def savePlot(self, figname):
		import matplotlib.pyplot as plt
		plt.savefig(figname)

	def showPlot(self):
		import matplotlib.pyplot as plt
		plt.show()

if __name__ == '__main__':
	import argparse
	cliParser = argparse.ArgumentParser(description='Pareto front plotter')
	cliParser.add_argument('filename', metavar='filename', type=str, help='name of the log file to plot')
	cliParser.add_argument('otherFilename0', metavar='otherFilename0', nargs='?', default=None, type=str, help='name of one more file to plot')
	cliParser.add_argument('-i', dest='interactive', action='store_const', const=True, default=False, help='only show interactive Matplotlib plot window')
	cliParser.add_argument('-V', dest='view', action='store_const', const=True, default=False, help='open Gwenview when done with plotting')
	cliArgs = cliParser.parse_args()

	if not cliArgs.interactive:
		matplotlib.use('Agg')

	if cliArgs.otherFilename0:
		p0 = ParetoPlotter(cliArgs.otherFilename0)
		p0.plot(colorPoints='y', colorLine='g', label=p0.filename, priority=1)
	p = ParetoPlotter(cliArgs.filename)
	p.plot(label='titular filename', title=p.filename)

	import matplotlib.pyplot as plt

	if cliArgs.otherFilename0:
		plt.legend()
	plt.grid()

	if cliArgs.interactive:
		plt.show()
	else:
		outfilename = cliArgs.filename + '.png'
		plt.savefig(outfilename)
		if cliArgs.view:
			import subprocess
			subprocess.call(['gwenview', outfilename])
