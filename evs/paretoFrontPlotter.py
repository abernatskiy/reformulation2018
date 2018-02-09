#!/usr/bin/python2

execfile('main.py')

pareto = evolver.updatePopulation()
nonpareto = filter(lambda x: x.__dominated__, evolver.population)

con = evolver.params['secondMinObj']

pareto = sorted(pareto, key=lambda x: x.score, reverse=False)

paretoScores = [ -1*x.score for x in pareto ]
paretoConns = [ con(x) for x in pareto ]
nonparetoScores = [ -1*x.score for x in nonpareto ]
nonparetoConns = [ con(x) for x in nonpareto ]

import matplotlib.pyplot as plt
import numpy as np

plt.plot(paretoScores, paretoConns, '-o', color='red')
plt.scatter(nonparetoScores, nonparetoConns, c='blue')

plt.xlabel('Minus fitness')
plt.ylabel('No of connections')
plt.title('Pareto front for sg 8.0 fg 4.0')
