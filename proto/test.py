#!/usr/bin/python3

from pprint import pprint

import netlist

# map node index to list of pairs (node, port)
nodes = {}

wire = -1

def init_wire (layer, sink, port):
	global wire
	i = str (wire)

	n = netlist.node ()
	n.links.append ([sink, port])
	n.layer = layer
	n.type = 'wire'

	nodes[i] = n
	wire = wire - 1

	return i

# 0. read netlist
def nodes_parse_line (nodes, line):
	source, sink, port = line.split ()
	port = int (port)

	for n in (source, sink):
		if not n in nodes:
			nodes[n] = netlist.node ()

	nodes[source].links.append ([sink, port])

	if nodes[source].type == 'output':
		nodes[source].type = 'gate'

	nodes[sink].ports = nodes[sink].ports + 1

	if nodes[sink].type == 'input':
		nodes[sink].type = 'output'

with open ('test.netlist', 'r') as f:
	for line in f:
		nodes_parse_line (nodes, line)

# 1. layer nodes
def layer_node (n):
	for link in n.links:
		sink = nodes[link[0]]

		if sink.layer <= n.layer:
			sink.layer = n.layer + 1
			layer_node (sink)

def layer_nodes (nodes):
	for n in nodes.values ():
		layer_node (n)

layer_nodes (nodes)

# 2. move outputs to last layer
def last_layer ():
	last = 0

	for n in nodes.values ():
		if last < n.layer:
			last = n.layer

	return last

def pool_out_outputs (nodes):
	last = last_layer ()

	for n in nodes.values ():
		if n.type == 'output':
			n.layer = last

pool_out_outputs (nodes)

# 3. add passthrough phantom nodes
def link_length (n, l):
	sink = nodes[l[0]]

	return sink.layer - n.layer

def add_phantoms (n):
	links = n.links
	n.links = []

	for l in links:
		if link_length (n, l) == 1:
			n.links.append (l)
		else:
			i = init_wire (n.layer + 1, l[0], l[1])
			n.links.append ([i, 1])

			add_phantoms (nodes[i])

real_nodes = list (nodes.values ())

for n in real_nodes:
	add_phantoms (n)

# 4. reduce phantom node count
def reduce_phantoms (n):
	wire = None

	links = n.links
	n.links = []

	for l in links:
		sink = nodes[l[0]]

		if sink.type != 'wire':
			n.links.append (l)
		elif wire is None:
			wire = sink
			n.links.append (l)
		else:
			wire.links.extend (sink.links)
			reduce_phantoms (wire)
			del nodes[l[0]]

for n in real_nodes:
	reduce_phantoms (n)

# distribute nodes into layers
def get_layers (nodes):
	layers = {}

	for n in nodes.values ():
		l = n.layer

		if not l in layers:
			layers[l] = []

		layers[l].append (n)

	return layers

layers = get_layers (nodes)

# 5. order nodes
def weight_node (n, weight):
	if not hasattr (n, 'y'):
		n.y = weight
		n.count = 1
	else:
		n.y += weight
		n.count += 1

def normalize_node (n):
	if hasattr (n, 'count'):
		n.y /= n.count
		del n.count

def weight_layer (i):
#	weight = 0
	netlist.dispose_layer_nodes (layers[i - 1])

	for n in layers[i - 1]:
		for l in n.links:
#			weight_node (nodes[l[0]], weight)
			weight_node (nodes[l[0]], n.y)

#		weight += 1.0

	for n in layers[i - 1]:
		for l in n.links:
			normalize_node (nodes[l[0]])

def weight_layers (layers):
	for i in range (1, len (layers)):
		weight_layer (i)
		list.sort (layers[i], key = lambda n: n.y)

weight_layers (layers)

# test
# pprint (layers)

# show schema
import cairo

width, height = netlist.dispose_nodes (layers)
surface = cairo.SVGSurface ("test.svg", width, height)
c = cairo.Context (surface)

c.set_line_width (1.3)

netlist.show_nodes (c, nodes)
netlist.show_links (c, nodes)

