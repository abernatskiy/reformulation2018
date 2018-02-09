import subprocess
import sys
from os.path import expanduser
from os.path import isdir
import os

eswclient = 'eswclientPrime'

dirs = [ d for d in os.listdir('.') if isdir(d) ]
home = expanduser("~")
file = open(home + '/evscripts/randints1421128240.dat', 'r')
seeds = []
for line in file:
	seeds.append(int(line))
oneTrueSeed = seeds[int(sys.argv[1])]

evalPipeName = '/tmp/evaluations' + str(oneTrueSeed) + '_pid' + str(os.getpid()) + '.pipe'
indivPipeName = '/tmp/individuals' + str(oneTrueSeed) + '_pid' + str(os.getpid()) + '.pipe'
subprocess.call(['/usr/bin/mkfifo', evalPipeName])
subprocess.call(['/usr/bin/mkfifo', indivPipeName])

for dir in dirs:
	os.chdir(dir)
	client = subprocess.Popen([home + '/anaconda/bin/python2.7', home + '/' + eswclient + '/runEvaluator.py', indivPipeName, evalPipeName])
	subprocess.call([home + '/anaconda/bin/python2.7', home + '/evs/mainConfig.py', evalPipeName, indivPipeName, str(oneTrueSeed), sys.argv[2]])
	client.send_signal(subprocess.signal.SIGTERM)
	subprocess.call(['/bin/bash', home + '/evscripts/modularityProcessors/computeFileQ.sh', 'bestIndividual' + str(oneTrueSeed) + '.log'])
	os.chdir('..')

subprocess.call(['/bin/rm', evalPipeName])
subprocess.call(['/bin/rm', indivPipeName])
