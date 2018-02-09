import subprocess
import sys
from os.path import expanduser

home = expanduser("~")
file = open(home + '/evscripts/randints1421128240.dat', 'r')
seeds = []
for line in file:
	seeds.append(int(line))
oneTrueSeed = seeds[int(sys.argv[1])]

subprocess.call(['/bin/bash', home + '/evscripts/modularityProcessors/computeFileQ.sh', 'bestIndividual' + str(oneTrueSeed) + '.log'])
