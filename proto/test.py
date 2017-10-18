#!/usr/bin/python3

from pprint import pprint

p = 8

# map node index to list of pairs (node, port)
nodes = {}

def init_node (i):
	nodes[i] = {'links': [], 'layer': 0, 'type': 'input', 'ports': 0}

wire = -1

def init_wire (layer, sink, port):
	global wire
	i = str (wire)

	nodes[i] = {'links': [[sink, port]], 'layer': layer, 'type': 'wire', 'ports': 0}
	wire = wire - 1

	return i

# 0. read netlist
with open ('test.netlist', 'r') as f:
	for line in f:
		source, sink, port = line.split ()
		port = int (port)

		for n in (source, sink):
			if not n in nodes:
				init_node (n)

		nodes[source]['links'].append ([sink, port])

		if nodes[source]['type'] == 'output':
			nodes[source]['type'] = 'gate'

		nodes[sink]['ports'] = nodes[sink]['ports'] + 1

		if nodes[sink]['type'] == 'input':
			nodes[sink]['type'] = 'output'

# map layer index to list of nodes
layers = {}

# 1. layer nodes
def layer_node (n):
	layer = n['layer']

	for link in n['links']:
		sink = nodes[link[0]]

		if sink['layer'] <= layer:
			sink['layer'] = layer + 1
			layer_node (sink)

for n in nodes.values ():
	layer_node (n)

# 2. move outputs to last layer
def last_layer ():
	last = 0

	for n in nodes.values ():
		if last < n['layer']:
			last = n['layer']

	return last

for n in nodes.values ():
	last = last_layer ()

	if n['type'] == 'output':
		n['layer'] = last

# 3. add passthrough phantom nodes
def link_length (n, l):
	sink = nodes[l[0]]

	return sink['layer'] - n['layer']

def add_phantoms (n):
	links = n['links']
	n['links'] = []

	for l in links:
		if link_length (n, l) == 1:
			n['links'].append (l)
		else:
			i = init_wire (n['layer'] + 1, l[0], l[1])
			n['links'].append ([i, 1])

			add_phantoms (nodes[i])

real_nodes = list (nodes.values ())

for n in real_nodes:
	add_phantoms (n)

# 4. reduce phantom node count
def reduce_phantoms (n):
	wire = None

	links = n['links']
	n['links'] = []

	for l in links:
		sink = nodes[l[0]]

		if sink['type'] != 'wire':
			n['links'].append (l)
		elif wire is None:
			wire = sink
			n['links'].append (l)
		else:
			wire['links'].extend (sink['links'])
			reduce_phantoms (wire)
			del nodes[l[0]]

for n in real_nodes:
	reduce_phantoms (n)

# distribute nodes into layers
for n in nodes.values ():
	l = n['layer']

	if not l in layers:
		layers[l] = []

	layers[l].append (n)

# dispose nodes
def dispose_layer_nodes (l):
	y = p

	for n in l:
		t = n['type']

		if t == 'input' or t == 'output':
			h = p
		elif t == 'wire':
			h = 0
		else:
			h = n['ports'] * p + p

		n['y'] = y
		n['h'] = h

		y = y + h + p

	return y

def dispose_nodes ():
	width  = p
	height = p

	for l in layers.values ():
		y = dispose_layer_nodes (l)

		if height < y:
			height = y

		for n in l:
			n['x'] = width

		width += (2 + 1 + 3) * p

	return width - 3 * p, height

# 5. order nodes
def weight_node (n, weight):
	if not 'y' in n:
		n['y'] = weight
		n['count']  = 1
	else:
		n['y'] += weight
		n['count']  += 1

def normalize_node (n):
	if 'count' in n:
		n['y'] /= n['count']
		del n['count']

def weight_layer (i):
#	weight = 0
	dispose_layer_nodes (layers[i - 1])

	for n in layers[i - 1]:
		for l in n['links']:
#			weight_node (nodes[l[0]], weight)
			weight_node (nodes[l[0]], n['y'])

#		weight += 1.0

	for n in layers[i - 1]:
		for l in n['links']:
			normalize_node (nodes[l[0]])

for i in range (1, len (layers)):
	weight_layer (i)
	list.sort (layers[i], key = lambda n: n['y'])

# test
# pprint (layers)

# show schema
import math
import cairo

def show_input (c, n):
	c.set_source_rgb (0, 0, 0)
	c.arc (n['x'] + p, n['y'] + p, p / 4, 0, math.pi * 2)
	c.rel_line_to (.75 * p, 0)
	c.stroke ()

def show_output (c, n):
	c.set_source_rgb (0, 0, 0)
	c.arc (n['x'] + p, n['y'] + p, p / 4, 0, math.pi * 2)
	c.rel_move_to (-.5  * p, 0)
	c.rel_line_to (-.75 * p, 0)
	c.stroke ()

def show_wire (c, n):
	c.set_source_rgb (0, 0, 0)
	c.move_to (n['x'], n['y'])
	c.rel_line_to (2 * p, 0)
	c.stroke ()

def show_gate (c, n):
	c.set_source_rgb (1, 1, .8)
	c.rectangle (n['x'], n['y'], 2 * p, n['h'])
	c.fill ()

	c.set_source_rgb (0, 0, 0)
	c.rectangle (n['x'], n['y'], 2 * p, n['h'])
	c.stroke ()

def show_node (c, n):
	t = n['type']

	if t == 'input':
		show_input (c, n)
	elif t == 'output':
		show_output (c, n)
	elif t == 'wire':
		show_wire (c, n)
	else:
		show_gate (c, n)

def show_nodes (c, nodes):
	for n in nodes.values ():
		show_node (c, n)

def show_node_links (c, n):
	c.set_source_rgb (.56, .69, .85)

	for l in n['links']:
		sink = nodes[l[0]]
		port = l[1]

		source_shift = p if n['type'] != 'wire' else 0
		sink_shift = port * p if sink['type'] != 'wire' else 0

		c.move_to (n['x'] + 2 * p, n['y'] + source_shift)
		c.line_to (sink['x'], sink['y'] + sink_shift)
		c.stroke ()

def show_links (c, nodes):
	for n in nodes.values ():
		show_node_links (c, n)

width, height = dispose_nodes ()
surface = cairo.SVGSurface ("test.svg", width, height)
c = cairo.Context (surface)

c.set_line_width (1.3)

show_nodes (c, nodes)
show_links (c, nodes)

