#!/usr/bin/python2

from subprocess import call
from math import pow

# fg 16 sg 4 - classical Braitenberg
# fg 8 sg 2 - nonmodular Braitenberg, with classical one performing suboptimally

randomSeedsFile = 'randints1416971160.dat'

forceGain = 8.0
sensorGain = 2.0

connectionCost = 0.0
print('Investigating the case of forceGain ' + str(forceGain) + ', sensorGain ' + str(sensorGain) + ', connection cost ' + str(connectionCost))
call(['./getFitnessTimeSeriesForParams.sh', str(forceGain), str(sensorGain), str(connectionCost), randomSeedsFile])

#for connectionCost in [pow(2.0, x) for x in range(14, 20, 2)]:
for connectionCost in [4096.0,6144.0,8192.0,12228.0,32768.0]:
	print('Investigating the case of forceGain ' + str(forceGain) + ', sensorGain ' + str(sensorGain) + ', connection cost ' + str(connectionCost))
	call(['./getFitnessTimeSeriesForParams.sh', str(forceGain), str(sensorGain), str(connectionCost), randomSeedsFile])

forceGain = 16.0
sensorGain = 4.0

connectionCost = 0.0
print('Investigating the case of forceGain ' + str(forceGain) + ', sensorGain ' + str(sensorGain) + ', connection cost ' + str(connectionCost))
call(['./getFitnessTimeSeriesForParams.sh', str(forceGain), str(sensorGain), str(connectionCost), randomSeedsFile])

#for connectionCost in [pow(2.0, x) for x in range(13, 24, 2)]:
for connectionCost in [786432.0,1048576.0,1310720.0]:
	print('Investigating the case of forceGain ' + str(forceGain) + ', sensorGain ' + str(sensorGain) + ', connection cost ' + str(connectionCost))
	call(['./getFitnessTimeSeriesForParams.sh', str(forceGain), str(sensorGain), str(connectionCost), randomSeedsFile])
