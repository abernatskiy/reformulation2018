import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

connwidth = 3

def defaultInputLabel(i):
	return 'i' + str(i+1)

def defaultOutputLabel(i):
	return 'o' + str(i+1)

def generateNodePositions(inDim, outDim, inputLabels=[defaultInputLabel], outputLabel=defaultOutputLabel):
	inputKinds = len(inputLabels)
	pos = {}
	for k in range(inputKinds):
		for i in range(inDim):
			pos[inputLabels[k](i)] = (0, inputKinds*i + k - float(inputKinds*inDim)/2)
	for j in range(outDim):
		pos[outputLabel(j)] = (1, inputKinds*j - float(inputKinds*outDim)/2)
	return pos

def alphaGen(weight):
	return np.abs(weight)
#	return np.power(np.abs(weight), 1.5)

def drawSubnetworkConnections(g, pos, controller, inputLabel=defaultInputLabel, outputLabel=defaultOutputLabel):
	inDim, outDim = controller.shape
	eExitatory = []
	eEColors = []
	eInhibitory = []
	eIColors = []
	for i in range(inDim):
		for j in range(outDim):
			if controller[i,j] != 0:
				curEdge = (inputLabel(i), outputLabel(j))
				g.add_edge(curEdge[0], curEdge[1])
				if controller[i,j] > 0:
					eExitatory.append(curEdge)
					eEColors.append(controller[i,j])
				else:
					eInhibitory.append(curEdge)
					eIColors.append(-1.*controller[i,j])
	for edge,alpha in zip(eExitatory,eEColors):
		nx.draw_networkx_edges(g, pos, edgelist=[edge], width=connwidth, edge_color='blue', alpha=alphaGen(alpha), arrows=True)
	for edge,alpha in zip(eInhibitory,eIColors):
		nx.draw_networkx_edges(g, pos, edgelist=[edge], width=connwidth, edge_color='red', alpha=alphaGen(alpha), arrows=True)

def drawSimpleController(controller, inputLabel=defaultInputLabel, outputLabel=defaultOutputLabel, filename='controller.png'):
	'''Makes a picture of a simple one layer feedforward network, given its weight matrix'''
	drawCompoundController([controller], inputLabels=[inputLabel], outputLabel=outputLabel, filename=filename)

def drawCompoundController(controllerList, inputLabels=[defaultInputLabel], outputLabel=defaultOutputLabel, filename='controller.png'):
	'''Makes a picture of a controller with several input types, each with its own weight matrix'''
	plt.figure(figsize=(6., 6.*len(controllerList)))
	inDim, outDim = controllerList[0].shape
	pos = generateNodePositions(inDim, outDim, inputLabels=inputLabels, outputLabel=outputLabel)
	g = nx.DiGraph()
	for controller, inputLabel in zip(controllerList, inputLabels):
		drawSubnetworkConnections(g, pos, controller, inputLabel=inputLabel, outputLabel=outputLabel)
	nx.draw_networkx_nodes(g, pos, node_size=3000, node_color='white')
	nx.draw_networkx_labels(g, pos, font_size=20, font_family='sans-serif')
	plt.axis('off')
	plt.savefig(filename)
	plt.clf()

# To test, run: drawCompoundController([np.array([[1,0,0.5],[-1,-0.1,1],[-1,-1,-1]]), np.array([[0.8,0.8,0],[-0.5,0,0],[1,1,1]])], inputNameMaps=[lambda x:'s'+str(x), lambda x:'p'+str(x)])
