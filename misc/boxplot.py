#!/usr/bin/env python2

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

errorsFrames = {}
morphologyNames = {'null': 'J=0', 'identity': 'J=I'}
for method in ['random', 'sparse']:
	errorsArray = np.array([], dtype=np.float)
	segmentsArray = np.array([], dtype=np.int)
	morphologyArray = np.array([], dtype=np.str)
	for segments in [3, 5, 10]:
		#fitnessDict[method][segments] = {}
		for morphology in ['null', 'identity']:
			#fitnessDict[method][segments][morphology] = -1*np.loadtxt('finalFitnesses/seg{}_morpology{}_method{}'.format(segments, morphology, method))
			curNpErrors = -1*np.loadtxt('finalFitnesses/seg{}_morpology{}_method{}'.format(segments, morphology, method))
			errorsArray = np.concatenate((errorsArray, curNpErrors))
			segmentsArray = np.concatenate((segmentsArray, [segments]*len(curNpErrors)))
			morphologyArray = np.concatenate((morphologyArray, [morphologyNames[morphology]]*len(curNpErrors)))
	errorsFrames[method] = pd.DataFrame({'morphology': morphologyArray, 'number of segments': segmentsArray, 'error': errorsArray})

for method in ['random', 'sparse']:
	#plt.figure(figsize=(5,3))
	sns.set(style='ticks')
	sns.boxplot(x='number of segments', y='error', hue='morphology', data=errorsFrames[method])
	plt.ylim(-0.25, 1.25)
	plt.savefig(method+'.png',dpi=600)
	plt.clf()
