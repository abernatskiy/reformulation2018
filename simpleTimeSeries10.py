from os.path import join, expanduser
from time import sleep
import subprocess
import os
import numpy as np
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
sys.path.append(join(expanduser('~'), 'morphMod'))

from matplotlib.colors import LogNorm

import pbsGridWalker.grid as gr
import pbsGridWalker.tools.algorithms as tal
import pbsGridWalker.tools.fsutils as tfs
import pbsGridWalker.tools.plotutils as tplt

import morphModRoutes as mmr
import classifiers
import gctools
import gccommons

# Tunable hyperparameters
numTrials = 100
segments = 10
# Optional definitions for pbsGridWalker that depend on the number of segments
pointsPerJob = 1
maxJobs = 400
queue = 'workq'
expectedWallClockTime = '30:00:00'

# Constant hyperparameters
evsDefaults = {'individual': 'compositeFixedProbabilities', 'evolver': 'cluneSimplifiedMorphologyControlIndividuals', 'communicator': 'chunkedUnixPipe',
               'compositeClass0': 'integerVectorSymmetricRangeMutations', 'probabilityOfMutatingClass0': 0.2,
               'lengthClass0': segments, 'initLowerLimitClass0': 0, 'initUpperLimitClass0': segments, 'lowerCapClass0': 0, 'upperCapClass0': segments,
               'mutationAmplitudeClass0': 1,
               'compositeClass1': 'trinaryWeights',
               'lengthClass1': 2*(segments**2), 'initLowerLimitClass1': -1, 'initUpperLimitClass1': 1, 'lowerCapClass1': -1, 'upperCapClass1': 1,
               'mutExplorationClass1': 0.8, 'mutInsDelRatioClass1': 1, 'mutationAmplitudeClass1': 1,
               'genStopAfter': 4000, 'populationSize': 200,
               'initialPopulationType': 'random', 'secondObjectiveProbability': 1.,
               'logParetoFront': 'yes', 'logBestIndividual': 'yes', 'logParetoFrontKeepAllGenerations': 'yes', 'logParetoFrontPeriod': 5, 'logParetoSize': 'yes',
               'backup': 'no', 'trackAncestry': 'no',
               'randomSeed': 0}
evsDefaults['logParetoFrontPeriod'] = 1 # overriding because the field in defaults gets changed during the scripts' autogeneration
arrowbotsDefaults = {'segments': segments, 'sensorAttachmentType': 'variable',
                     'simulationTime': 10., 'timeStep': 0.1,
                     'integrateError': 'false', 'writeTrajectories': 'false'}
arrowbotInitialConditions = [[0]*segments]*segments # segmentsXsegments null matrix
arrowbotTargetOrientations = [ [1 if i==j else 0 for i in range(segments)] for j in range(segments) ] # segmentsXsegments identity matrix
# Optional definitions for pbsGridWalker that are constant
involvedGitRepositories = mmr.involvedGitRepositories
# dryRun = False

### Required pbsGridWalker definitions
computationName = 'simpleTimeSeries_N' + str(segments)

gcvsrandGrid = gr.Grid1d('compositeClass0', ['integerVectorSymmetricRangeMutations', 'integerVectorRandomJumps'])*gr.Grid1d('probabilityOfMutatingClass0', [0.2])
constmorphGrid = gr.Grid1d('compositeClass0', ['integerVectorSymmetricRangeMutations'])*gr.Grid1d('probabilityOfMutatingClass0', [0.0])
nonRSGrid = gcvsrandGrid.concatenate(constmorphGrid)
# parametricGrid = nonRSGrid*numTrials + gr.Grid1dFromFile('randomSeed', mmr.randSeedFile, size=len(nonRSGrid)*numTrials)

# Since the order of iteration is not guaranteed in Python, different random seed sets get assigned to different non-RS points on different machines.
# To circumvent that, I pickle the grid (produced by the commented line above) on the machine that does the calculations and unpickle it on the data processing machine.
import pickle
with open(join(mmr.morphModPath, 'rawgrid'), 'r') as rgf:
	parametricGrid = pickle.load(rgf)

for par in parametricGrid.paramNames():
	evsDefaults.pop(par)

def prepareEnvironment(experiment):
	gccommons.prepareEnvironment(experiment)

def runComputationAtPoint(worker, params):
	return gccommons.runComputationAtPoint(worker, params,
		evsDefaults, arrowbotsDefaults,
		arrowbotInitialConditions,
		arrowbotTargetOrientations)

def plotTTCvsMMMD(experiment):
	import scipy
	fitnessThreshold = -8

	def TTCvsMMMD(gridPoint):
		if not (gridPoint['compositeClass0'] == 'integerVectorSymmetricRangeMutations' and gridPoint['probabilityOfMutatingClass0'] == 0.2):
			return

		# determining the time of convergence
		bilogFileName = 'bestIndividual{}.log'.format(gridPoint['randomSeed'])
		bilog = np.loadtxt(bilogFileName)
		toc = None # time of convergence
								# TOME OF CONVERGENCE
		for i in range(bilog.shape[0]):
			if -1.*bilog[i,1] <= fitnessThreshold:
				toc = i
				break
		if toc is None:
			with open('../results/nonconverged runs', 'a') as ncrf:
				ncrf.write(str(gridPoint['randomSeed']) + '\n')
			return

		# making a scatter of points of TTC vs MMMD
		with open('../results/ttcvsmmmd', 'a') as tmfile:
			for i in range(evsDefaults['genStopAfter']+1):
				tmfile.write('{} {}\n'.format(toc-i, gctools.minParetoFrontHammingDistanceToMMM(i)))

	experiment.executeAtEveryGridPointDir(TTCvsMMMD)

	os.chdir('results')

	ttcmmmddata = np.loadtxt('ttcvsmmmd')
	mmmd = ttcmmmddata[:,1]
	ttc = ttcmmmddata[:,0]
	mmmdrange = [0,6]
	ttcrange = [ min(ttc), max(ttc) ]
	mmmdbins = 6
	ttcbins = 100

	xdat = mmmd
	ydat = ttc
	xrange = mmmdrange
	yrange = ttcrange
	xbins = mmmdbins
	ybins = ttcbins

	# https://stackoverflow.com/questions/10439961
	xyrange = [ xrange, yrange ]
	bins = [xbins, ybins]
	thresh = 1

	hh, locx, locy = scipy.histogram2d(xdat, ydat, range=xyrange, bins=bins)
	posx = np.digitize(xdat, locx)
	posy = np.digitize(ydat, locy)

	# select points within the histogram
	ind = (posx > 0) & (posx <= bins[0]) & (posy > 0) & (posy <= bins[1])
	hhsub = hh[posx[ind] - 1, posy[ind] - 1] # values of the histogram where the points are
	xdat1 = xdat[ind][hhsub < thresh] # low density points
	ydat1 = ydat[ind][hhsub < thresh]
	hh[hh < thresh] = np.nan # fill the areas with low density by NaNs

	fig, ax = plt.subplots(figsize=(7,6))
	cax = fig.add_axes() # https://stackoverflow.com/questions/32462881

	#im = ax.imshow(np.flipud(hh.T),cmap='jet',extent=np.array(xyrange).flatten(), interpolation='none', origin='upper',norm=LogNorm(vmin=1, vmax=10000))
	im = ax.imshow(np.flipud(hh.T),cmap='jet',extent=np.array(xyrange).flatten(), interpolation='none', origin='upper',norm=LogNorm(vmin=1))

	cb = fig.colorbar(im, cax=cax)
	cb.set_label('# of points')

	ax.plot(xdat1, ydat1, '.',color='darkblue')

	ax.set_xlabel(r'$\mu$', x=1.0, fontsize=20)
	ax.set_ylabel(r'$\tau_{conv}$', y=1.0, fontsize=20)
	# ax.set_ylim([0,420])

	ax.set_aspect(0.006)
	plt.savefig('ttcvsmmmd.png', dpi=300)
	plt.clf()

	os.chdir('..')

def plotErrorTSs(experiment, prefixFun):
	import shutil

	gridFileNamePrefix = prefixFun

	##### Extracting and plotting fitness time series #####

	xlabel = r'$T$'
	#figureDims = [7,4]
	figureDims = None
	xlimit = evsDefaults['genStopAfter']
	margins = 0.5
	strips = 'conf95'

	title = None
	legendLocation = 1

	def fitnessFileName(gp):
		return gridFileNamePrefix(gp) + '_fitness'
	def columnExtractor(gp):
		outFile = fitnessFileName(gp)
		subprocess.call('cut -d \' \' -f 2 bestIndividual*.log | tail -n +4 | tr \'\n\' \' \' >> ../results/' + outFile, shell=True)
		subprocess.call('echo >> ../results/' + outFile, shell=True)
	experiment.executeAtEveryGridPointDir(columnExtractor)

	os.chdir('results')

	ylabel = r'$\log_{10} E$'
	forcedYLabelPos = [0.05, 1.]
	ylimit = None

	title = None
	dataDict = {gridFileNamePrefix(p): -1.*np.loadtxt(fitnessFileName(p)) for p in nonRSGrid}

	# Plotting averages
	yscale = 'lin'
	xscale = 'lin'

	tplt.plotAverageTimeSeries(dataDict, ylabel, 'errorComparisonLinLin.png', title=title, legendLocation=legendLocation, xlabel=xlabel, xlimit=xlimit, ylimit=ylimit, xscale=xscale, yscale=yscale, margins=margins, strips=strips, figureDims=figureDims, forcedYLabelPos=forcedYLabelPos)
	xscale = 'log'
	tplt.plotAverageTimeSeries(dataDict, ylabel, 'errorComparisonLogLin.png', title=title, legendLocation=legendLocation, xlabel=xlabel, xlimit=xlimit, ylimit=ylimit, xscale=xscale, yscale=yscale, margins=margins, strips=strips, figureDims=figureDims, forcedYLabelPos=forcedYLabelPos)

	# Plotting the trajectory scatter
	alpha = 0.3
	yscale = 'lin'

	xscale = 'lin'
	tplt.plotAllTimeSeries(dataDict, ylabel, 'errorAllTrajectoriesLinLog.png', title=title, legendLocation=legendLocation, xlabel=xlabel, xlimit=xlimit, ylimit=ylimit, xscale=xscale, yscale=yscale, margins=margins, alpha=alpha, figureDims=figureDims, forcedYLabelPos=forcedYLabelPos)
	xscale = 'log'
	tplt.plotAllTimeSeries(dataDict, ylabel, 'errorAllTrajectoriesLogLog.png', title=title, legendLocation=legendLocation, xlabel=xlabel, xlimit=xlimit, ylimit=ylimit, xscale=xscale, yscale=yscale, margins=margins, alpha=alpha, figureDims=figureDims, forcedYLabelPos=forcedYLabelPos)

	plt.clf()

	os.chdir('..')

def plotMinMMMDistTSs(experiment, prefixFun):
	'''Extracting and plotting time series for distance to the maximally modular morphology (MMM)'''

	xlabel = r'$T$'
	figureDims = [7,4]
	#figureDims = None
	xlimit = evsDefaults['genStopAfter']
	margins = 0.5
	strips = 'conf95'

	title = None
	legendLocation = 1

	gridFileNamePrefix = prefixFun
	def minMMMDistFileName(gridPoint):
		return '../results/' + gridFileNamePrefix(gridPoint) + '_minMMMDist'
	def generateMinMMMDistTimeSeries(gridPoint):
		minMMMDistTS = [ gctools.minParetoFrontHammingDistanceToMMM(gen) for gen in range(1, evsDefaults['genStopAfter']+1) ]
		filename = minMMMDistFileName(gridPoint)
		with open(filename, 'a') as file:
			file.write(' '.join(map(str, minMMMDistTS)) + '\n')
	experiment.executeAtEveryGridPointDir(generateMinMMMDistTimeSeries)

	os.chdir('results')
	ylabel = r'$\mu$'
	ylimit = None

	title = None
	dataDict = {gridFileNamePrefix(p): np.loadtxt(minMMMDistFileName(p)) for p in nonRSGrid}

	# Plotting averages in linear time scales on y
	yscale = 'lin'
	xscale = 'lin'
	tplt.plotAverageTimeSeries(dataDict, ylabel, 'minMMMDistTS.png', title=title, legendLocation=legendLocation, xlabel=xlabel, xlimit=xlimit, ylimit=ylimit, xscale=xscale, yscale=yscale, margins=margins, strips=strips, figureDims=figureDims)

	plt.clf()

	os.chdir('..')

def processResults(experiment):
	tfs.makeDirCarefully('results', maxBackups=100)
	plotTTCvsMMMD(experiment)

	def gridFileNamePrefix(gridPoint):
		if gridPoint['probabilityOfMutatingClass0'] == 0.2:
			if gridPoint['compositeClass0'] == 'integerVectorSymmetricRangeMutations':
				return 'move_sensor_by_1_segment'
			elif gridPoint['compositeClass0'] == 'integerVectorRandomJumps':
				return 're-generate_morphology'
		elif gridPoint['probabilityOfMutatingClass0'] == 0 and gridPoint['compositeClass0'] == 'integerVectorSymmetricRangeMutations':
				return 'no_morphological_mutation'
		raise ValueError('Wrong point {} in the non-RS grid'.format(gridPoint))

	plotErrorTSs(experiment, gridFileNamePrefix)
	plotMinMMMDistTSs(experiment, gridFileNamePrefix)
