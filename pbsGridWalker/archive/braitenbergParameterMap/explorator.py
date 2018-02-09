#!/usr/bin/python2

from subprocess import call
from math import pow

for forceGain in [pow(2.0, x) for x in range(-5, 10)]:
	for sensorGain in [pow(2.0, x) for x in range(-5, 10)]:
		print 'Investigating the case of forceGain ' + str(forceGain) + ', sensorGain ' + str(sensorGain)
		call(['./findNetworksForParams.sh', str(forceGain), str(sensorGain)])

