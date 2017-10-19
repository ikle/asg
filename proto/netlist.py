#!/usr/bin/python3

import math
import cairo

p = 8

class node (object):
	def __init__ (o):
		o.links = []
		o.layer = 0
		o.type = 'input'
		o.ports = 0

	def show_input (o, c):
		c.set_source_rgb (0, 0, 0)
		c.arc (o.x + p, o.y + p, p / 4, 0, math.pi * 2)
		c.rel_line_to (.75 * p, 0)
		c.stroke ()

	def show_output (o, c):
		c.set_source_rgb (0, 0, 0)
		c.arc (o.x + p, o.y + p, p / 4, 0, math.pi * 2)
		c.rel_move_to (-.5  * p, 0)
		c.rel_line_to (-.75 * p, 0)
		c.stroke ()

	def show_wire (o, c):
		c.set_source_rgb (0, 0, 0)
		c.move_to (o.x, o.y)
		c.rel_line_to (2 * p, 0)
		c.stroke ()

	def show_gate (o, c):
		c.set_source_rgb (1, 1, .8)
		c.rectangle (o.x, o.y, 2 * p, o.h)
		c.fill ()

		c.set_source_rgb (0, 0, 0)
		c.rectangle (o.x, o.y, 2 * p, o.h)
		c.stroke ()

	def show_node (o, c):
		if o.type == 'input':
			o.show_input (c)
		elif o.type == 'output':
			o.show_output (c)
		elif o.type == 'wire':
			o.show_wire (c)
		else:
			o.show_gate (c)

	def show_node_links (o, c, nodes):
		c.set_source_rgb (.56, .69, .85)

		for l in o.links:
			sink = nodes[l[0]]
			port = l[1]

			source_shift = p if o.type != 'wire' else 0
			sink_shift = port * p if sink.type != 'wire' else 0

			c.move_to (o.x + 2 * p, o.y + source_shift)
			c.line_to (sink.x, sink.y + sink_shift)
			c.stroke ()

def show_nodes (c, nodes):
	for o in nodes.values ():
		o.show_node (c)

def show_links (c, nodes):
	for o in nodes.values ():
		o.show_node_links (c, nodes)

# dispose nodes
def dispose_layer_nodes (layer):
	y = p

	for n in layer:
		t = n.type

		if t == 'input' or t == 'output':
			h = p
		elif t == 'wire':
			h = 0
		else:
			h = n.ports * p + p

		n.y = y
		n.h = h

		y = y + h + p

	return y

def dispose_nodes (layers):
	width  = p
	height = p

	for layer in layers.values ():
		y = dispose_layer_nodes (layer)

		if height < y:
			height = y

		for n in layer:
			n.x = width

		width += (2 + 1 + 3) * p

	return width - 3 * p, height
