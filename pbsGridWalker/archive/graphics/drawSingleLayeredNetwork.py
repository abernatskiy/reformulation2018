#!/usr/bin/python2

try:
    import matplotlib.pyplot as plt
    import networkx as nx
except:
    raise

import sys

weights = [ int(s) for s in sys.argv[1:] ]

if(len(sys.argv) != 5):
    raise

G = nx.DiGraph()
G.add_nodes_from(['in0','in1','out0','out1'])

pos = {'in0':(0,1),
       'in1':(1,1),
       'out0':(1,0),
       'out1':(0,0)}

G.add_edge('in0', 'out0', weight=weights[0])
G.add_edge('in0', 'out1', weight=weights[1])
G.add_edge('in1', 'out0', weight=weights[2])
G.add_edge('in1', 'out1', weight=weights[3])

eexitatory = [ (u,v) for (u,v,d) in G.edges(data=True) if d['weight'] == 1 ]
einhibitory = [ (u,v) for (u,v,d) in G.edges(data=True) if d['weight'] == -1 ]

nx.draw_networkx_nodes(G, pos, node_size=3000, node_color='white')
nx.draw_networkx_edges(G, pos, edgelist=eexitatory, width=1, edge_color='green', arrows=True)
nx.draw_networkx_edges(G, pos, edgelist=einhibitory, width=1, edge_color='red', arrows=True)
nx.draw_networkx_labels(G,pos,font_size=20,font_family='sans-serif')

plt.axis('off')
plt.savefig(reduce(lambda x,y: x+y, sys.argv[1:]) + '.png')
