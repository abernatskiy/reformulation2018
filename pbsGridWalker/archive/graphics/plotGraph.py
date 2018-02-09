#!/usr/bin/python2

annTopology = [4,-2,2]
inputAnnotations = ['<p<SUB>l</SUB>>', '<p<SUB>r</SUB>>', '<l<SUB>l</SUB>>', '<l<SUB>r</SUB>>']
outputAnnotations = ['<m<SUB>0</SUB>>', '<m<SUB>1</SUB>>']

import numpy as np
import pydot

def getNumLinks(topology):
	if topology != []:
		acc = 0
		for iLayer in range(len(topology)-1):
			acc += abs(topology[iLayer])*abs(topology[iLayer+1])
			if topology[iLayer+1] < 0:
				acc += abs(topology[iLayer+1])*abs(topology[iLayer+1])
		return acc
	else:
		return None

def getPositions(topology):
	scalingFactor = 1
	curY = 1
	x = []
	y = []
	for l in map(abs, topology):
#		x.append([ -1.*float(l-1)/2 + float(i) for i in range(l)])
		x.append([ 1 + i for i in range(l)])
		y.append(curY)
		curY += 2
	return [ [ xq*scalingFactor for xq in xl ] for xl in x ], [ yq*scalingFactor for yq in y ]

def getWeights(netdesc, topol):
	links = []
	curpos = 0
	for iLayer in range(len(topol)-1):
		inNeu = abs(topol[iLayer])
		outNeu = abs(topol[iLayer+1])
		curordinary = np.array(netdesc[curpos:(curpos+inNeu*outNeu)])
		curordinary = curordinary.reshape(inNeu, outNeu)
		curpos += inNeu*outNeu
		if topol[iLayer+1] < 0:
			curhidden = np.array(netdesc[curpos:(curpos+outNeu*outNeu)])
			curhidden = curhidden.reshape(outNeu, outNeu)
			curpos += outNeu*outNeu
		else:
			curhidden = None
		links.append((curordinary, curhidden))
	return links

def printWeights(nwWeights):
	counter = 0
	for wgts, hwgts in nwWeights:
		counter += 1
		print('Layer %02d' % counter + ':')
		print('\n' + repr(wgts))
		print('\n' + repr(hwgts))
	print('')


import sys

numLinks = getNumLinks(annTopology)
xn, yn = getPositions(annTopology)

while True:
	mline = sys.stdin.readline()
	if not mline:
		break
	if mline[0] == '#':
		continue

	fields = mline.split()
	nwDesc = map(float, fields[-1*numLinks:])
	nwID = int(fields[-1*(numLinks+1)])
	nwMetadata = fields[:-1*(numLinks+1)]

	nwWeights = getWeights(nwDesc, annTopology)

	graph = pydot.Dot(graph_type='digraph')

	# Making input nodes
	# See node attribute list at http://www.graphviz.org/doc/info/attrs.html
	upperNodes = []
	for i in range(abs(annTopology[0])):
		curNodeName = 'i' + str(i)
		curNodePos = '\"' + str(xn[0][i]) + ',' + str(yn[0]) + '!\"'
		print curNodePos
		graph.add_node(pydot.Node(curNodeName, label=inputAnnotations[i], shape='circle', pos=curNodePos, pin=True, width=0.75))
		upperNodes.append(curNodeName)

	# For each layer below the input
	for l in range(1, len(annTopology)):
		curNodes = []
		upperLayerSize = abs(annTopology[l-1])
		curLayerSize = abs(annTopology[l])
		# Add all nodes
		for j in range(curLayerSize):
			curNodeName = 'h'+str(j)+'_'+str(l) if l<(len(annTopology)-1) else 'm'+str(j)
			curNodePos = '\"' + str(xn[l][j]) + ',' + str(yn[l]) + '!\"'
			print curNodePos
			curNodes.append(curNodeName)
			graph.add_node(pydot.Node(curNodeName, shape='circle', pos=curNodePos, pin=True, width=0.75))
		# Add connections from the upper layer to the current layer
		wgts, hwgts = nwWeights[l-1]
		for i in range(upperLayerSize):
			for j in range(curLayerSize):
				if wgts[i][j] != 0:
					graph.add_edge(pydot.Edge(upperNodes[i], curNodes[j], color='red' if wgts[i][j]<0 else 'blue'))
		# If the topology involves recursion, add connection from the current layer to itself
		if annTopology[l] < 0:
			for i in range(curLayerSize):
				for j in range(curLayerSize):
					if hwgts[i][j] != 0:
						graph.add_edge(pydot.Edge(curNodes[i], curNodes[j], color='red' if hwgts[i][j]<0 else 'blue'))
		upperNodes = curNodes

	graph.write_png(str(nwID)+'.png')

