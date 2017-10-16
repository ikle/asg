# The Automatic Schematic Generation Problem

Split the solution of the Automatic Schematic Generation (ASG) problem
into several stages to simplify description and further implementation.
At the first stage, consider acyclic logic circuits, built from
elementary gates.

## First Stage Basis

Let the node is an element with n inputs and m outputs: n:m element for
short. In the first stage, we define three kinds of elements:

1.  input node:  0:1 element;
2.  output node: 1:0 element;
3.  logic gate:  n:1 element.

We will represent the input and output elements as small circles, and
logic gates as rectangles. The inputs are always on the left, and the
outputs on the right.

At the first stage we will use the simplest netlist format from the rows
of triples of natural numbers, where the first two numbers are the
indices of the source and sink nodes, respectively, and the third is the
sink node input index.

## Acyclic Schema Layering

Distribute the nodes along the layers so that the layer number for some
node is the maximum number of edges from the given node to an input node.

## Add Passthrough Phantom Nodes

Let the length of the edge is the difference of the layer numbers of the
sink node and the source node. Divide each edge with a length l, greater
than one, on l edges, inserting a phantom passthrough nodes between them,
distributing them accordingly on layers.

## Reduce Phantom Node Count

Combine all phantom nodes in the same layer to one if they are connected
by an edge to the same node from the previous layer. (This can be done at
the same time as the previous step.)

## Order Nodes in Layers

1.  Assign weights to each node in the first layer starting from zero
    with a step of one in the order of the definition of the inputs.
2.  For each subsequent layer, define the node weight as the arithmetic
    mean of the weights of the nodes from the previous layer, from which
    an edge exists to the given node.
3.  Sort the nodes by weight in each layer.

## Make Edges Orthogonal

1.  For each two adjacent layers, create a strip for each output port of
    lower layer.
2.  On each of strip, mark the points with the coordinates corresponding
    to the output port of the strip and each of the input ports into
    which there is an edge from this output port.
3.  Сonnect these points by lines with each other. 
4.  Сonnect the points on the strip to the corresponding ports.

## Minimize Edge Crossing

1.  Swap two adjacent strips, if the number of intersections decreases.
2.  Repeat the previous step as far as possible.
3.  Join every two adjacent strips if their segments will not intersect.


