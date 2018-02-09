#!/usr/bin/env python2

import numpy as np
import sys

f = np.loadtxt(sys.argv[1])
print(str(50. - np.sum(f[:,0]*f[:,1])/np.sum(f[:,0])))
