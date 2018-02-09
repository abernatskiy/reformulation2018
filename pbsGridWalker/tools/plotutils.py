import numpy as np
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pickle

colors = ['red', 'blue', 'yellow', 'green', 'cyan', 'violet', 'lime', 'peru', 'maroon', 'sienna', 'indianred']

def _applyCosmetics(title, xlabel, ylabel, xlimits, ylimits, legendLocation, figureDims=None, forcedXLabelPos=None, forcedYLabelPos=None):
	fontsize = 20
	# plt.xlabel(xlabel) # default center alignment
	plt.xlabel(xlabel, horizontalalignment='right', x=1.0, fontsize=fontsize) # use this to align the label to the right
	# plt.ylabel(ylabel) # default center position and rotation
	plt.ylabel(ylabel, horizontalalignment='right', y=1.0, rotation=0, fontsize=fontsize) # label aligned to the top and written horizontally

	ax = plt.gca()
	if not forcedXLabelPos is None:
		ax.xaxis.set_label_coords(forcedXLabelPos[0], forcedXLabelPos[1])
	if not forcedYLabelPos is None:
		ax.yaxis.set_label_coords(forcedYLabelPos[0], forcedYLabelPos[1])

	if not legendLocation is None:
		plt.legend(loc=legendLocation)
	if xlimits:
		plt.xlim(xlimits[0], xlimits[1])
	if title:
		plt.title(title)
	if ylimits[0] != ylimits[1]:
		plt.ylim(ylimits[0], ylimits[1])

	if figureDims:
		plt.rcParams["figure.figsize"] = figureDims


def _forceSetRatio(rat):
	ax = plt.gca()
	fig  = plt.gcf()
	fwidth = fig.get_figwidth()
	fheight = fig.get_figheight()

	# get the axis size and position in relative coordinates
	# this gives a BBox object
	bb = ax.get_position()

	# calculate them into real world coordinates
	axwidth = fwidth * (bb.x1 - bb.x0)
	axheight = rat * fheight * (bb.y1 - bb.y0)
	# if the axis is wider than tall, then it has to be narrowe
	if axwidth > axheight:
		# calculate the narrowing relative to the figure
		narrow_by = (axwidth - axheight) / fwidth
		# move bounding box edges inwards the same amount to give the correct width
		bb.x0 += narrow_by / 2
		bb.x1 -= narrow_by / 2
	# else if the axis is taller than wide, make it vertically smaller
	# works the same as above
	elif axheight > axwidth:
		shrink_by = (axheight - axwidth) / fheight
		bb.y0 += shrink_by / 2
		bb.y1 -= shrink_by / 2

	ax.set_position(bb)

def _choosePlottingFunction(xscale, yscale):
	if xscale == 'lin':
		if yscale == 'lin':
			return plt.plot
		elif yscale == 'log':
			return plt.semilogy
	elif xscale == 'log':
		if yscale == 'lin':
			return plt.semilogx
		elif yscale == 'log':
			return plt.loglog
	raise NotImplementedError('Cannot provide an appropriate function for xscale={} and yscale={}'.format(xscale, yscale))

def _applyMargins(axisType, limits, margins):
	if axisType == 'lin':
		return [limits[0]-margins, limits[1]+margins]
	elif axisType == 'log':
		return [limits[0]*(1.-margins), limits[1]*(1.+margins)]
	else:
		raise NotImplementedError('Cannot apply margins to a {} axis'.format(axisType))

def plotAverageTimeSeries(samplesDict, ylabel, outFile, title=None,
	strips='conf95', xlabel='Time', xlimit=None, ylimit=None,
	disableStrips=False, legendLocation=4, dpi=300, figsize=None,
	xscale='lin', yscale='lin', margins=0.1, timeRange=None, figureDims=None, forcedXLabelPos=None, forcedYLabelPos=None, marker=None):
	'''Plots averages of several random time series. The samples must represented
     as a numpy matrix (each row is a sample) and stored as values in the
	   samplesDict dictionary. The keys of the dictionary will be used to annotate
	   the plot via legend. Error data is provided in the form of strips
	   surrounding each everage plot. What exactly the strip represents is
	   controlled by the strips option:
	     strips='conf95' (default) - 95% confidence interval (gaussian assumption)
	     strips='stderr' - raw standard error of the sum
	  Strips can be disabled by setting disableStrips to true, in which case they
	  are going to be replaced with errorbars around the points. This is useful
	  when the xlimit is low.
		The output is written in PNG format to outFile.
	'''
	import stats
	colorIdx = 0
	limits = [np.inf, -np.inf]
	plotFunc = _choosePlottingFunction(xscale, yscale)
	for tsname in sorted(samplesDict.keys()):
		tssamples = samplesDict[tsname]
		tsavg = np.mean(tssamples, axis=0)
		tsstderr = stats.timeSeriesStderr(tssamples)
		if strips == 'conf95':
			tsstderr *= 1.96
		elif strips == 'stderr':
			pass
		elif strips is None:
			pass
		else:
			raise ValueError('Unsupported strip type {}. Supported types: conf95, stderr'.format(strips))
		lower = tsavg - tsstderr
		upper = tsavg + tsstderr
		limits = [ min(limits[0], min(lower)), max(limits[1], max(upper)) ]

		if timeRange is None:
			timeRange = np.arange(0,len(tsavg))
		if disableStrips:
			plt.errorbar(timeRange, tsavg, color=colors[colorIdx], yerr=tsstderr, label=tsname)
		else:
			if not strips is None:
				plotFunc(timeRange, lower, timeRange, upper, color=colors[colorIdx], alpha=0.5)
				plt.fill_between(timeRange, lower, upper, where=upper>=lower, facecolor=colors[colorIdx], alpha=0.3, interpolate=True)
			plotFunc(timeRange, tsavg, color=colors[colorIdx], label=tsname, marker=marker)

		colorIdx += 1
	limits = _applyMargins(yscale, limits, margins)
	_applyCosmetics(title, xlabel, ylabel, [0, xlimit] if xlimit else None, [0, ylimit] if ylimit else limits, legendLocation, figureDims=figureDims, forcedXLabelPos=forcedXLabelPos, forcedYLabelPos=forcedYLabelPos)

	fig = matplotlib.pyplot.gcf()
	if figsize:
		fig.set_size_inches(figsize[0], figsize[0])
	fig.savefig(outFile, dpi=dpi)
	plt.close()

def plotAllTimeSeries(samplesDict, ylabel, outFile, title=None, xlabel='Time',
	xlimit=None, ylimit=None, legendLocation=4, dpi=300, alpha=0.1, figsize=None,
	xscale='lin', yscale='lin', margins=0.1, timeRange=None, figureDims=None, forcedXLabelPos=None, forcedYLabelPos=None):
	'''Generates a plot of all time series generated by several processes. The
	   time series samples must represented as numpy matrices (each row is a
	   time series) and stored as values in the samplesDict dictionary. The keys
	   of the dictionary will be interpreted as generating processes' labels and
	   used to annotate the plot via legend.
		The output is written in PNG format to outFile.
	'''
	colorIdx = 0
	limits = [np.inf, -np.inf]
	plotFunc = _choosePlottingFunction(xscale, yscale)
	for tsname, tssamples in samplesDict.items():
		limits = [ min(limits[0], np.min(tssamples)), max(limits[1], np.max(tssamples)) ]
		if timeRange is None:
			timeRange = np.arange(0, tssamples.shape[1])
		plotFunc(timeRange, tssamples[0,:], color=colors[colorIdx], alpha=alpha, label=tsname)
		for trajIdx in range(1, tssamples.shape[0]):
			plotFunc(timeRange, tssamples[trajIdx,:], color=colors[colorIdx], alpha=alpha)
		colorIdx += 1
	limits = _applyMargins(yscale, limits, margins)
	_applyCosmetics(title, xlabel, ylabel, [0, xlimit] if xlimit else None, [0, ylimit] if ylimit else limits, legendLocation, figureDims=figureDims, forcedXLabelPos=forcedXLabelPos, forcedYLabelPos=forcedYLabelPos)
	fig = matplotlib.pyplot.gcf()
	if figsize:
		fig.set_size_inches(figsize[0], figsize[0])
	fig.savefig(outFile, dpi=dpi)
	plt.close()

def plotComputationVariableAgainstParameter(experiment, variableName, variableGenerator, parameterName,
                                    statisticsAlong=['randomSeed'], fieldNames=None, transform=lambda x: x,
                                    title=None, margins=0.5, xscale='lin', yscale='lin', legendLocation=1,
                                    xlimit=None, ylimit=None, xlabel=None, ylabel=None, figureDims=None, strips='conf95', forcedXLabelPos=None, forcedYLabelPos=None, marker=None):
	'''Allows the experimenter to plot a variable (or a vector of those)
     (computed from the results of the computation by the function
     variableGenerator) against one of the parameters of the grid.
     The remaining parameters can be averaged over (those are given by
     the statisticsAlong list of parameter names) or used as conditions,
     such that for every set of conditions a separate plot is generated.
  '''
	from copy import deepcopy
	def pDictStr(pdict):
		return '_'.join([ '{}{}'.format(pn, pdict[pn]) for pn in sorted(pdict.keys()) ])
	def dataFileName(gridPoint):
		freeParamVals = deepcopy(gridPoint)
		for rpn in statisticsAlong:
			freeParamVals.pop(rpn, None) # second arg ensures that the function will work even if there are no statistical params in the grid point, see https://stackoverflow.com/questions/15411107
		return '../results/' + pDictStr(freeParamVals) + '_' + variableName
	def generateTimeSlices(gridPoint):
		vars = variableGenerator(gridPoint)
		with open(dataFileName(gridPoint), 'a') as file:
			file.write(' '.join(map(str, vars)) + '\n')
#	experiment.executeAtEveryGridPointDir(generateTimeSlices)

	os.chdir('results')

	parameterVals = set()
	for p in experiment.grid:
		parameterVals.add(p[parameterName])
	parameterVals = sorted(list(parameterVals))

	# Generating a representation of condition (i.e. all the parameters that are not statistical or on the horizontal axis) as a set of hashable tuples of tuples
	tCondPoints = set()
	for p in experiment.grid:
		condPoint = deepcopy(p)
		condPoint.pop(parameterName)
		for sp in statisticsAlong:
			condPoint.pop(sp)
		tCondPoints.add(tuple(sorted(condPoint.iteritems())))

	# Reading the data back and making a plot at every conditions point
	numCurves = -1
	numCurvesKnown = False
	for tCondPoint in tCondPoints:
		condPoint = dict(tCondPoint)

		rdata = [] if not numCurvesKnown else [ [] for i in range(numCurves) ]
		for pv in parameterVals:
			fullCondPoint = deepcopy(condPoint)
			fullCondPoint[parameterName] = pv
			fullCondData = np.loadtxt(dataFileName(fullCondPoint), ndmin=2)

			if not numCurvesKnown:
				numCurves = fullCondData.shape[1]
				rdata = [ [] for i in range(numCurves) ]
				if not fieldNames:
					curveNames = [ 'field {}'.format(fn) for fn in range(numCurves) ]
				elif len(fieldNames) == numCurves:
					curveNames = fieldNames
				else:
					raise ValueError('Field names iterable has wrong length')
				numCurvesKnown = True

			for curveNum in range(numCurves):
				rdata[curveNum].append(fullCondData[:,curveNum])

			#print('param val: ' + str(pv) + '\n' + 'condPoint: ' + str(condPoint) + '\n\n\n')
			#print('rdata: ' + str(rdata) + '\n\n\n')
			#print('fullCondData: ' + str(fullCondData))
			#import sys
			#sys.exit(0)

		data = { curveNames[cn]: transform(np.stack(rdata[cn]).T) for cn in range(numCurves) }
		pointStr = '{}_vs_{}_at_{}'.format(variableName, parameterName, pDictStr(condPoint))

		with open(pointStr + '.p', 'w') as pfile:
			pickle.dump(data, pfile)

		ylabel = ylabel if ylabel else variableName
		xlabel = xlabel if xlabel else parameterName
		plotAverageTimeSeries(data, ylabel, pointStr + '.png',
		                      timeRange=parameterVals,
		                      xlabel=xlabel, title=title,
		                      legendLocation=legendLocation, margins=margins,
		                      xlimit=xlimit, ylimit=ylimit,
		                      xscale=xscale, yscale=yscale, figureDims=figureDims, strips=strips, forcedXLabelPos=forcedXLabelPos, forcedYLabelPos=forcedYLabelPos, marker=marker)

	os.chdir('..')
