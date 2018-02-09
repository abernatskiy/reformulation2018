#!/usr/bin/python2

import drawnet as dn

import numpy as np
import sys

genotype = sys.argv[1].split(' ')
id = int(genotype[0])
n = np.sqrt((len(genotype)-1)/2)
if float(int(n)) != n:
	raise ValueError('Malformed genotype')
n = int(n)

tsn = np.array(genotype[1:n*n+1], dtype=float).reshape(n,n)
psn = np.array(genotype[1:n*n+1], dtype=float).reshape(n,n)

#print str(tsn)
#print str(psn)

dn.drawCompoundController([tsn,psn],
                           inputLabels=[lambda x: 's'+str(x+1), lambda x: 'p'+str(x+1)],
                           outputLabel=lambda x: 'm'+str(x+1),
                           filename='genotype_'+str(id)+'.png')
