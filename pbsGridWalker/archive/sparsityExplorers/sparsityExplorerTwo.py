import subprocess
import sys
from os.path import expanduser
from os.path import isdir
import os

dirs = [ d for d in os.listdir('.') if isdir(d) ]
home = expanduser("~")
file = open(home + '/evscripts/randints1421128240.dat', 'r')
seeds = []
for line in file:
	seeds.append(int(line))
oneTrueSeed = seeds[int(sys.argv[1])]
oneTrueDir = dirs[int(sys.argv[1])]

evalPipeName = '/tmp/evaluations' + str(oneTrueSeed) + '.pipe'
indivPipeName = '/tmp/individuals' + str(oneTrueSeed) + '.pipe'
subprocess.call(['/usr/bin/mkfifo', evalPipeName])
subprocess.call(['/usr/bin/mkfifo', indivPipeName])

client = subprocess.Popen([home + '/anaconda/bin/python2.7', home + '/eswclient/runEvaluator.py', indivPipeName, evalPipeName])

os.chdir(oneTrueDir)
subprocess.call([home + '/anaconda/bin/python2.7', home + '/evs/mainConfig.py', evalPipeName, indivPipeName, str(oneTrueSeed), sys.argv[2]])
subprocess.call(['/bin/bash', home + '/evscripts/modularityProcessors/computePrefixQ.sh', 'seed' + str(oneTrueSeed)])
os.chdir('..')

client.send_signal(subprocess.signal.SIGTERM)

subprocess.call(['/bin/rm', evalPipeName])
subprocess.call(['/bin/rm', indivPipeName])
