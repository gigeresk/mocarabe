# -*- coding: future_fstrings -*-
import random

from gurobipy import *
import timeit
from simanneal import Annealer

# from placement_visualizer import visualize_placement
import math


def where(array, value_target):
    # assert( len(set(array)) == len(array) )

    for ix, val in enumerate(array):
        if val == value_target:
            return ix


def initialize_state_ok(
    Nx, Ny, ii, dataflow_hypergraph, partitioned_op_map, type="topological"
):
    """No placement constraints yet"""
    """ strategies: topological triangle, random, dfg-aware sort...idk"""

    # partitioned_op_map: think that's dfg node-> partition.
    # first attempt: get a topological sort, and place
    # things by growing a rectangle in the bottom right.... TODO
    # dfg_v_to_partition_id = partitioned_op_map.dfg_v_to_partition_id
    from networkx.algorithms.dag import topological_sort

    # number of nodes (or could be # of IOs+ mult partitions)
    initial_state = [0] * len(dataflow_hypergraph.ordered_node_id_list())

    # \n
    # for ix in range( len( initial_state ) ): initial_state[ix] = ix # should be unique id
    every_pe = []
    for x in range(Nx):
        for y in range(Ny):
            every_pe.append((x, y))
    # multiplier_areas =[]# [(1,0),(1,2),(1,4),(1,6),(1,8)]
    # adder_areas = []#[(0,4),(0,5),(0,7),(0,9)]

    # io_areas = [x for x in every_pe if x not in multiplier_areas and x not in adder_areas] #io_areas = every_pe - multiplier_areas - adder_areas
    # initialize initial_state to place multipliers
    node_operators = dataflow_hypergraph.extract_node_arithmetic_operators()
    node_in = dataflow_hypergraph.extract_input_nodes()
    node_out = dataflow_hypergraph.extract_output_nodes()

    mul_nodes = []
    add_nodes = []

    # for node, operator in node_operators.items():
    #     if operator == '*':
    #         mul_nodes.append( node )
    #     elif operator == '+':
    #         add_nodes.append( node )

    # operations_per_mul_operator = math.ceil( (len(mul_nodes)+len(add_nodes) +  / len(multiplier_areas) )
    # operations_per_add_operator = math.ceil( len(add_nodes) / len(adder_areas) )
    # operations_per_operator = math.ceil(( len(node_operators)+ len(node_in)+len(node_out))/(Nx*Ny))
    pe_ix = 0
    for ix, pe in enumerate(initial_state):
        initial_state[ix] = pe_ix
        pe_ix += 1
        pe_ix = pe_ix % (Nx * Ny)

    mul_nodes = []
    add_nodes = []
    io_nodes = []
    # for i, mul_node in enumerate(mul_nodes):
    #     start_xy = multiplier_areas[ i//operations_per_mul_operator ]
    #     initial_state[int(mul_node)] =  start_xy[0] + start_xy[1] * Nx

    # for i, add_node in enumerate(add_nodes):
    #     start_xy = adder_areas[ i//operations_per_add_operator ]
    #     initial_state[int(add_node)] =  start_xy[0] + start_xy[1] * Nx

    # # IO
    # io_nodes = []
    # node_in_and_out = {**node_in, **node_out }
    # for node, in_or_out in node_in_and_out.items():
    #     io_nodes.append( node )

    # operations_per_io_operator = math.ceil( len(io_nodes) / ( Nx*Ny - len(multiplier_areas) - len(adder_areas) ) )

    # for i, io_node in enumerate(io_nodes):
    #     start_xy = io_areas[ i // operations_per_io_operator ]
    #     initial_state[int(io_node)] =  start_xy[0] + start_xy[1] * Nx

    # for i, add_node in enumerate(add_nodes):
    #     start_xy = adder_areas[ i//operations_per_add_operator ]
    #     initial_state[int(add_node)] =  start_xy[0] + start_xy[1] * Nx

    print(
        f"Starting energy: {debug_energy(dataflow_hypergraph, mul_nodes, add_nodes, io_nodes, initial_state, Nx, Ny, ii):} "
    )

    return initial_state, mul_nodes, add_nodes, io_nodes


def torus_min_distance_xy(sourcexy, sinkxy, Nx, Ny):
    source_x = sourcexy % Nx
    source_y = sourcexy // Nx
    sink_x = sinkxy % Nx
    sink_y = sinkxy // Nx

    # assert( source_x < Nx )
    # assert( sink_x < Nx )
    # assert( source_y < Ny )
    # assert( sink_y < Ny )

    if source_x <= sink_x and source_y <= sink_y:
        """
        --------------
        |  / >> snk  |
        |  ^         |
        | src        |
        --------------
        """
        # no rollover
        return ((sink_x - source_x), (sink_y - source_y))
    elif source_x > sink_x and source_y <= sink_y:
        """
        --------------
        |  snk       |
        |  ^         |
        |>>/    src>>|
        --------------
        """
        return ((Nx + sink_x - source_x), (sink_y - source_y))
    elif source_x <= sink_x and source_y > sink_y:
        """
        --------------
        |  ^         |
        |  src       |
        |  />>>>snk  |
        --------------
        """
        # \n
        return ((sink_x - source_x), (Ny + sink_y - source_y))
    else:
        """
        ---------------
        |          ^  |
        |         src |
        |  />>snk     |
        |>>/^       />|
        --------------
        """
        return ((Nx - source_x + sink_x), (Ny + -source_y + sink_y))


class AnnealingClusterPlacer(Annealer):
    # pass extra data (the distance matrix) into the constructor
    def __init__(
        self, state, ii, dataflow_hypergraph, Nx, Ny, mul_nodes, add_nodes, io_nodes
    ):  # TODO GET RID OF NX NY
        self.Nx = Nx
        self.Ny = Ny
        self.ii = ii
        self.dataflow_hypergraph = dataflow_hypergraph

        self.mul_nodes = mul_nodes
        self.add_nodes = add_nodes
        self.io_nodes = io_nodes

        super(AnnealingClusterPlacer, self).__init__(state)  # important!

    def move(self):
        initial_energy = self.energy()

        a = random.randint(0, len(self.state) - 1)
        b = random.randint(0, len(self.state) - 1)
        self.state[a], self.state[b] = self.state[b], self.state[a]
        # if str(a) in self.mul_nodes and str(b) in self.mul_nodes:
        #     self.state[a], self.state[b] = self.state[b], self.state[a]
        # elif str(a) in self.add_nodes and str(b) in self.add_nodes:
        #     self.state[a], self.state[b] = self.state[b], self.state[a]
        # elif str(a) in self.io_nodes and str(b) in self.io_nodes:
        #     self.state[a], self.state[b] = self.state[b], self.state[a]
        # elif str(a) in self.io_nodes and str(b) in self.add_nodes:
        #     self.state[a], self.state[b] = self.state[b], self.state[a]
        # elif str(a) in self.add_nodes and str(b) in self.io_nodes:
        #     self.state[a], self.state[b] = self.state[b], self.state[a]

        # print('moved')
        return self.energy() - initial_energy

    def energy(self):

        # dfg_node_to_logical_pe = self.partitioned_netlist.dfg_v_to_partition_id

        current_sink = 0
        e = 0
        for hyperedge_id in list(
            self.dataflow_hypergraph.ordered_hyperedge_id_iterator()
        ):
            net = self.dataflow_hypergraph.get_hyperedge_attributes(hyperedge_id)
            source = net["tail"][0]

            # source_pe = dfg_node_to_logical_pe[int( source )]
            for sink in net["head"]:
                # sink_pe = dfg_node_to_logical_pe[ int( sink ) ]

                current_sink = current_sink + 1
                # //ii is to account for ii>1
                ii = self.ii
                source_x = self.state[int(source) // ii] % self.Nx
                source_y = self.state[int(source) // ii] // self.Nx
                sink_x = self.state[int(sink) // ii] % self.Nx
                sink_y = self.state[int(sink) // ii] // self.Nx
                min_distance_x = abs(sink_x - source_x)
                min_distance_y = abs(sink_y - source_y)
                # linear
                # e = e + in_distance_xy[0]+min_distance_xy[1]
                # square

                e = e + (min_distance_x + 1) * (min_distance_y + 1)
        return e


class AnnealingNotSurePlacer(Annealer):
    # pass extra data (the distance matrix) into the constructor
    def __init__(
        self, state, dataflow_hypergraph, Nx, Ny, ii, mul_nodes, add_nodes, io_nodes
    ):  # TODO GET RID OF NX NY
        self.Nx = Nx
        self.Ny = Ny
        self.ii = ii
        self.dataflow_hypergraph = dataflow_hypergraph

        # self.mul_nodes = mul_nodes
        # self.add_nodes = add_nodes
        # self.io_nodes = io_nodes

        super(AnnealingNotSurePlacer, self).__init__(state)  # important!

    def move(self):
        initial_energy = self.energy()

        a = random.randint(0, len(self.state) - 1)
        b = random.randint(0, len(self.state) - 1)
        self.state[a], self.state[b] = self.state[b], self.state[a]
        # if str(a) in self.mul_nodes and str(b) in self.mul_nodes:
        #     self.state[a], self.state[b] = self.state[b], self.state[a]
        # elif str(a) in self.add_nodes and str(b) in self.add_nodes:
        #     self.state[a], self.state[b] = self.state[b], self.state[a]
        # elif str(a) in self.io_nodes and str(b) in self.io_nodes:
        #     self.state[a], self.state[b] = self.state[b], self.state[a]
        # elif str(a) in self.io_nodes and str(b) in self.add_nodes:
        #     self.state[a], self.state[b] = self.state[b], self.state[a]
        # elif str(a) in self.add_nodes and str(b) in self.io_nodes:
        #     self.state[a], self.state[b] = self.state[b], self.state[a]

        # print('moved')
        return self.energy() - initial_energy

    def energy(self):

        # dfg_node_to_logical_pe = self.partitioned_netlist.dfg_v_to_partition_id

        current_sink = 0
        e = 0
        for hyperedge_id in list(
            self.dataflow_hypergraph.ordered_hyperedge_id_iterator()
        ):
            net = self.dataflow_hypergraph.get_hyperedge_attributes(hyperedge_id)
            source = net["tail"][0]

            # source_pe = dfg_node_to_logical_pe[int( source )]
            for sink in net["head"]:
                # sink_pe = dfg_node_to_logical_pe[ int( sink ) ]

                current_sink = current_sink + 1

                min_distance_xy = torus_min_distance_xy(
                    self.state[int(source)] // self.ii,
                    self.state[int(sink)] // self.ii,
                    self.Nx,
                    self.Ny,
                )
                # linear
                # e = e + in_distance_xy[0]+min_distance_xy[1]
                # square

                e = e + (min_distance_xy[0] + 1) * (min_distance_xy[1] + 1)

        return e


def debug_energy(
    dataflow_hypergraph, mul_nodes, add_nodes, io_nodes, state, Nx, Ny, ii
):
    e = 0
    print("Nx=" + str(Nx) + ", Ny=" + str(Ny))

    # dfg_node_to_logical_pe = partitioned_netlist.dfg_v_to_partition_id

    current_sink = 0
    for hyperedge_id in list(dataflow_hypergraph.ordered_hyperedge_id_iterator()):
        net = dataflow_hypergraph.get_hyperedge_attributes(hyperedge_id)
        source = net["tail"][0]

        # source_pe = dfg_node_to_logical_pe[ int( source ) ]
        for sink in net["head"]:
            # sink_pe = dfg_node_to_logical_pe[ int( sink ) ]

            current_sink = current_sink + 1

            min_distance_xy = torus_min_distance_xy(
                state[int(source) // ii], state[int(sink) // ii], Nx, Ny
            )
            # linear
            # e = e + in_distance_xy[0]+min_distance_xy[1]
            # square

            e = e + (min_distance_xy[0] + 1) * (min_distance_xy[1] + 1)

            # print( f'from {source} at {state[source_pe]}=({state[source_pe] % Nx},{state[source_pe] // Nx}) to {sink} at {state[sink_pe]}=({state[sink_pe] % Nx},{state[sink_pe] // Nx}) : {min_distance_xy[0] + min_distance_xy[1]}' )

    return e
