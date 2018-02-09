#!/usr/bin/python2

import numpy as np
from scipy.linalg import sqrtm

def kmatrix(N):
	return np.array([ [ 1 if j<=i else 0 for j in range(N) ] for i in range(N) ])

def optKMatrix(N):
	K = kmatrix(N)
	return K.T.dot(np.linalg.inv(sqrtm(K.dot(K.T))))

if __name__ == '__main__':
	import drawnet as dn
	controllerSizes = [2,4]
	controllerTypes = ['fullyDistributed', 'fullyCentralized']
	beta = 3
	betaFactor = 1./np.sqrt(beta)
	for s in controllerSizes:
		targetSensorsNetwork = betaFactor*optKMatrix(s)
		# drawing the optimal feedback
		dn.drawSimpleController(-1.*kmatrix(s)*targetSensorsNetwork,
		                            inputLabel=lambda x: 'e'+str(x+1),
		                            outputLabel=lambda x: 'm'+str(x+1),
		                            filename='lqc_feedback'+str(s)+'.png')
		for t in controllerTypes:
			if t == 'fullyDistributed': # every sensors is attached to its own segment
				proprioceptiveNetwork = np.zeros((s,s))
			elif t == 'fullyCentralized': # all sensors are on the fixed (base) segment
				proprioceptiveNetwork = targetSensorsNetwork.dot(-1.*kmatrix(s))
			else:
				raise ValueError('Unknown controller type')
			print(repr(targetSensorsNetwork))
			print(repr(proprioceptiveNetwork))
			# drawing the controller itself
			dn.drawCompoundController([targetSensorsNetwork,
			                            proprioceptiveNetwork],
			                            inputLabels=[lambda x: 's'+str(x+1), lambda x: 'p'+str(x+1)],
			                            outputLabel=lambda x: 'm'+str(x+1),
			                            filename='lqc_'+t+str(s)+'.png')
