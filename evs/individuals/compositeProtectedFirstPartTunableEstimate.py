import numpy as np
import __builtin__

from compositeProtectedFirstPart import Individual as CompositeProtectedFirstPartIndividual

                                                                                
class Individual(CompositeProtectedFirstPartIndividual):
	# t['toFloat'].update(['timeEstimateCoefficient', 'timeEstimatePower', 'timeEstimatePower', 'timeEstimateWidth'])
	def controllerTimeLimit(self):
		connectionCost = len(filter(lambda x: x!=0, self.parts[1].values))
		return __builtin__.timeEstimateCoefficient*np.power(float(connectionCost), __builtin__.timeEstimatePower)
