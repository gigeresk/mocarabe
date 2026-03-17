import abc
import random
import itertools
from simanneal import Annealer

from mocarabe.placement_visualizer import visualize_placement


def initialize_state(dfg_v_to_partition_id, Nx, Ny):

    initial_state = [0] * Nx*Ny
    for ix in range(len(initial_state)):
        initial_state[ix] = ix

    return initial_state


def topographical_swap(dataflow_hypergraph, partitioned_op_map, dfg_v_to_partition_id, Nx, Ny, state, swap_rounds=3, type='topological'):
    ''' No placement constraints yet '''

    from networkx.algorithms.dag import topological_sort

    # go through every dfg node, compare.  if before, swap

    for swap_round in range(swap_rounds):
        for node_i in dataflow_hypergraph.ordered_node_id_list():
            for node_j in dataflow_hypergraph.ordered_node_id_list():

                node_i = node_i
                node_j = node_j
                if node_i == node_j:
                    continue

                i_is_topo_precedent = dataflow_hypergraph.is_topo_precedent(
                    node_i, node_j)
                j_is_topo_precedent = dataflow_hypergraph.is_topo_precedent(
                    node_j, node_i)

                i_node_partition = dfg_v_to_partition_id[int(node_i)]
                i_node_pe = state[i_node_partition]

                j_node_partition = dfg_v_to_partition_id[int(node_j)]
                j_node_pe = state[j_node_partition]

                i_node_x = i_node_pe % Nx
                i_node_y = i_node_pe // Nx
                j_node_x = j_node_pe % Nx
                j_node_y = j_node_pe // Nx

                if i_is_topo_precedent:  # if i comes before j in the dataflow graph
                    if (i_node_x > j_node_x and i_node_y > j_node_y):  # if i is dominated by j
                        state[j_node_partition], state[i_node_partition] = state[i_node_partition], state[j_node_partition]
                elif j_is_topo_precedent:
                    if (j_node_x > i_node_x and j_node_y > i_node_y):
                        state[j_node_partition], state[i_node_partition] = state[i_node_partition], state[j_node_partition]

    return state


def debug_energy(dataflow_hypergraph, partitioned_netlist, dfg_v_to_partition_id, state, Nx, Ny):
    e = 0
    for hyperedge_id in list(dataflow_hypergraph.ordered_hyperedge_id_iterator()):
        net = dataflow_hypergraph.get_hyperedge_attributes(hyperedge_id)
        source = net['tail'][0]
        source_pe = dfg_v_to_partition_id[int(source)]
        for sink in net['head']:
            sink_pe = dfg_v_to_partition_id[int(sink)]

            min_distance_xy = torus_min_distance_xy(
                state[source_pe], state[sink_pe], Nx, Ny)

            e = e + (min_distance_xy[0] + 1) * (min_distance_xy[1] + 1)
    return e

# TODO docstring


def toroidal_range(source, sink, max_):
    if source <= sink:
        return list(range(source+1, sink+1))
    if source > sink:
        return list(range(source, max_)) + list(range(0, sink))


def torus_min_distance_xy(sourcexy, sinkxy, Nx, Ny):
    ''' (x,y) Manhattan Distance between two points (x+y) on a toroidal Nx*Ny grid '''
    source_x = sourcexy % Nx
    source_y = sourcexy // Nx
    sink_x = sinkxy % Nx
    sink_y = sinkxy // Nx

    assert (source_x < Nx)
    assert (sink_x < Nx)
    assert (source_y < Ny)
    assert (sink_y < Ny)

    if (source_x <= sink_x and source_y <= sink_y):
        '''
        --------------
        |  / >> snk  |
        |  ^         |
        | src        |
        --------------
        '''
        return ((sink_x - source_x), (sink_y - source_y))
    elif (source_x > sink_x and source_y <= sink_y):
        '''
        --------------
        |  snk       |
        |  ^         |
        |>>/    src>>|
        --------------
        '''
        return ((Nx + sink_x - source_x), (sink_y - source_y))
    elif (source_x <= sink_x and source_y > sink_y):
        '''
        --------------
        |  ^         |
        |  src       |
        |  />>>>snk  |
        --------------
        '''
        return ((sink_x - source_x), (Ny + sink_y - source_y))
    else:
        '''
        ---------------
        |          ^  |
        |         src |
        |  />>snk     |
        |>>/^       />|
        --------------
        '''
        return ((Nx - source_x + sink_x), (Ny - source_y + sink_y))


class AbstractAnnealingPlacer(Annealer):
    # historical notes
    # memoized nets, saved 96% of runtime lol (not including other opts).
    # memozied torus distance, 30% runtime saved on gaussian unroll 2
    # flattened the memoized nets so that one element was a source-dest-pair even with high fanout, saved ~1s
    # how to reduce random?
    # switched from...
    # a = random.randint(0, len(self.state) - 1)
    # to
    # a = int( (len(self.state)-1) * random.random())
    # saved some time, about a second on my example!  didn't do comprehensive comparison
    # doing all this improved runtime from start of mocarabe.py to end of anneal() from 1m26s to around 12.5s: 85.5% decrease
    # pass extra data (the distance matrix) into the constructor

    __metaclass__ = abc.ABCMeta

    def __init__(self, state, dataflow_hypergraph, partitioned_netlist, Nx, Ny, dfg_v_to_partition_id, viz_placement_dir=False):
        super(AbstractAnnealingPlacer, self).__init__(state)

        self.partitioned_netlist = partitioned_netlist
        self.Nx, self.Ny = Nx, Ny
        self.dataflow_hypergraph = dataflow_hypergraph
        self.dfg_v_to_partition_id = dfg_v_to_partition_id
        self.viz_placement_dir = viz_placement_dir

        self.update_count = lambda c=itertools.count(): next(c)
        self.memoized_source_pe_and_dest_partitions = []

        for hyperedge_id in list(self.dataflow_hypergraph.ordered_hyperedge_id_iterator()):
            net = self.dataflow_hypergraph.get_hyperedge_attributes(
                hyperedge_id)
            source = net['tail'][0]
            source_pe = self.dfg_v_to_partition_id[int(source)]
            for sink in net['head']:
                self.memoized_source_pe_and_dest_partitions.append(
                    (source_pe, self.dfg_v_to_partition_id[int(sink)]))

        self.memoized_source_pe_and_dest_partitions = tuple(
            self.memoized_source_pe_and_dest_partitions)
        self.memoized_torus_distance = [
            [0 for a in range(Nx*Ny)] for b in range(Nx*Ny)]
        self.memoized_torus_distance_squared = [
            [0 for a in range(Nx*Ny)] for b in range(Nx*Ny)]

        for source in range(Nx*Ny):
            for dest in range(Nx*Ny):
                tmp = self.memoized_torus_distance[source][dest] = torus_min_distance_xy(
                    source, dest, Nx, Ny)
                self.memoized_torus_distance_squared[source][dest] = (
                    tmp[0]+1)*(tmp[1]+1)

    def move(self):
        a = int((len(self.state)-1) * random.random())
        b = int((len(self.state)-1) * random.random())

        self.state[a], self.state[b] = self.state[b], self.state[a]

        return

    @abc.abstractmethod
    def energy(self):
        pass

    # def update(self, step, T, E, acceptance, improvement):

    #     print(step,T,E,acceptance,improvement)
    #     if self.viz_placement_dir:
    #         file_dest = self.viz_placement_dir + f"/place_{str(self.update_count()).zfill(4)}.svg"
    #         dfg_node_to_pe_xy = {}
    #         for node, pe_id in enumerate( self.state ):
    #             dfg_node_to_pe_xy[node] = ( pe_id % self.Nx, pe_id // self.Nx )
    #         visualize_placement( self.dataflow_hypergraph, self.Nx, self.Ny, dfg_node_to_pe_xy, file_dest, energy=E, kill=True )

    #     self.default_update( step, T, E, acceptance, improvement )


class QuadraticWirelengthAnnealingPlacer(AbstractAnnealingPlacer):
    def __init__(self, state, dataflow_hypergraph, partitioned_netlist, Nx, Ny, dfg_v_to_partition_id, viz_placement_dir=False):  # TODO GET RID OF NX NY
        super(QuadraticWirelengthAnnealingPlacer, self).__init__(state, dataflow_hypergraph,
                                                                 partitioned_netlist, Nx, Ny, dfg_v_to_partition_id, viz_placement_dir)

    def energy(self):
        e = 0
        for source_partition, dest_partition in self.memoized_source_pe_and_dest_partitions:
            e += self.memoized_torus_distance_squared[self.state[source_partition]
                                                      ][self.state[dest_partition]]
        return e


class LinearWirelengthAnnealingPlacer(AbstractAnnealingPlacer):
    def __init__(self, state, dataflow_hypergraph, partitioned_netlist, Nx, Ny, dfg_v_to_partition_id, viz_placement_dir=False):  # TODO GET RID OF NX NY
        super(LinearWirelengthAnnealingPlacer, self).__init__(state, dataflow_hypergraph,
                                                              partitioned_netlist, Nx, Ny, dfg_v_to_partition_id, viz_placement_dir)

    def energy(self):
        e = 0
        for source_partition, dest_partition in self.memoized_source_pe_and_dest_partitions:
            e += sum(self.memoized_torus_distance[self.state[source_partition]]
                     [self.state[dest_partition]])
        return e


class AnnealingCongestionAwarePlacer(Annealer):
    # pass extra data (the distance matrix) into the constructor

    ''' going from [[0 for x in range( self.Ny )] for x in range( self.Nx )] to [[0] * self.Ny ] * self.Nx gave
    savings from 5.2s to 3.8s in energy().  then 2.27 by memoizing dataflow graph. apparently, 0.203 for not resetting net_congestion every time?
    down to 0.1 memoizing torus

    This gave me the same result as above for one, would be good to experiment.
    I got C=2 with this but only C=3 with above on this benchmark: python3 mocarabe.py -dfg hls/int_gaussian -II 1 -C 1 --place_time 1 --sched_method ILP -T 1 -iod 1 -ard 1 --unroll 3

    '''

    def __init__(self, state, dataflow_hypergraph, partitioned_netlist, Nx, Ny, dfg_v_to_partition_id, viz_placement_dir=False):  # TODO GET RID OF NX NY
        super(AnnealingCongestionAwarePlacer, self).__init__(state)
        self.dataflow_hypergraph = dataflow_hypergraph
        self.partitioned_netlist = partitioned_netlist
        self.Nx = Nx
        self.Ny = Ny
        self.dfg_v_to_partition_id = dfg_v_to_partition_id
        self.viz_placement_dir = viz_placement_dir
        self.update_count = lambda c=itertools.count(): next(c)

        self.memoized_source_pe_and_dest_partitions = []
        # memoize tail(source)/head(dest) nodes, as ints.
        for hyperedge_id in list(self.dataflow_hypergraph.ordered_hyperedge_id_iterator()):
            net = self.dataflow_hypergraph.get_hyperedge_attributes(
                hyperedge_id)
            source = net['tail'][0]
            source_pe = self.dfg_v_to_partition_id[int(source)]

            # not exactly the same as non-routing-aware placer
            dest_pes = []
            for sink in net['head']:
                dest_pes.append(self.dfg_v_to_partition_id[int(sink)])

            self.memoized_source_pe_and_dest_partitions.append(
                (source_pe, dest_pes))

        self.memoized_Nx_toroidal_range = [
            [0 for a in range(Nx)] for b in range(Nx)]
        for source in range(Nx):
            for dest in range(Nx):
                self.memoized_Nx_toroidal_range[source][dest] = toroidal_range(
                    source, dest, Nx)
        self.memoized_Ny_toroidal_range = [
            [0 for a in range(Ny)] for b in range(Ny)]
        for source in range(Ny):
            for dest in range(Ny):
                self.memoized_Ny_toroidal_range[source][dest] = toroidal_range(
                    source, dest, Ny)

    def move(self):
        a = int((len(self.state)-1) * random.random())
        b = int((len(self.state)-1) * random.random())

        self.state[a], self.state[b] = self.state[b], self.state[a]

        return

    def energy(self):
        ''' Bad for high-fanout, good for everything else (maybe: unproven) '''
        # XY ROUTING
        congestion_h = [[0] * self.Ny] * self.Nx
        congestion_v = [[0] * self.Ny] * self.Nx

        for source_partition, dest_partitions in self.memoized_source_pe_and_dest_partitions:
            for dest_partition in dest_partitions:
                source_x = self.state[source_partition] % self.Nx
                source_y = self.state[source_partition] // self.Nx
                sink_x = self.state[dest_partition] % self.Nx
                sink_y = self.state[dest_partition] // self.Nx

                for x_to_traverse in self.memoized_Nx_toroidal_range[source_x][sink_x]:
                    congestion_h[x_to_traverse][source_y] += 1

                for y_to_traverse in self.memoized_Ny_toroidal_range[source_y][sink_y]:
                    congestion_v[sink_x][y_to_traverse] += 1
        e = 0
        for x in range(self.Nx):
            for y in range(self.Ny):
                e += congestion_h[x][y] + congestion_v[x][y]

        return e

    # def update(self, step, T, E, acceptance, improvement):

    #     print(step,T,E,acceptance,improvement)
    #     if self.viz_placement_dir:
    #         file_dest = self.viz_placement_dir + f"/place_{str(self.update_count()).zfill(4)}.svg"
    #         dfg_node_to_pe_xy = {}
    #         for node, pe_id in enumerate( self.state ):
    #             dfg_node_to_pe_xy[node] = ( pe_id % self.Nx, pe_id // self.Nx )
    #         visualize_placement( self.dataflow_hypergraph, self.Nx, self.Ny, dfg_node_to_pe_xy, file_dest, energy=E, kill=True )

        # self.default_update( step, T, E, acceptance, improvement )


def bbox_generator(sourcexy, sinkxy, Nx, Ny):
    ''' (x,y) Manhattan Distance between two points (x+y) on a toroidal Nx*Ny grid '''
    source_x = sourcexy % Nx
    source_y = sourcexy // Nx
    sink_x = sinkxy % Nx
    sink_y = sinkxy // Nx

    assert (source_x < Nx)
    assert (sink_x < Nx)
    assert (source_y < Ny)
    assert (sink_y < Ny)

    x_to_increment = []
    y_to_increment = []

    if (source_x <= sink_x and source_y <= sink_y):
        '''
        --------------
        |  / >> snk  |
        |  ^         |
        | src        |
        --------------
        '''

        x_to_increment = list(range(source_x, sink_x+1))
        y_to_increment = list(range(source_y, sink_y+1))
        ret = []
        for x in x_to_increment:
            for y in y_to_increment:
                ret.append((x, y))
        return tuple(ret)  # x_to_increment, y_to_increment
        # return (( sink_x - source_x ), ( sink_y - source_y ))
    elif (source_x > sink_x and source_y <= sink_y):
        '''
        --------------
        |  snk       |
        |  ^         |
        |>>/    src>>|
        --------------
        '''

        x_to_increment = list(range(source_x, Nx)) + list(range(0, sink_x+1))
        y_to_increment = list(range(source_y, sink_y+1))
        ret = []
        for x in x_to_increment:
            for y in y_to_increment:
                ret.append((x, y))
        return tuple(ret)  # x_to_increment, y_to_increment
        # return (( Nx + sink_x - source_x ) , ( sink_y - source_y ))
    elif (source_x <= sink_x and source_y > sink_y):
        '''
        --------------
        |  ^         |
        |  src       |
        |  />>>>snk  |
        --------------
        '''
        x_to_increment = list(range(source_x, sink_x+1))
        y_to_increment = list(range(source_y, Ny)) + list(range(0, sink_y+1))
        ret = []
        for x in x_to_increment:
            for y in y_to_increment:
                ret.append((x, y))
        return tuple(ret)  # x_to_increment, y_to_increment
        # return (( sink_x - source_x ) , ( Ny + sink_y - source_y ))
    else:
        '''
        ---------------
        |          ^  |
        |         src |
        |  />>snk     |
        |>>/^       />|
        --------------
        '''

        x_to_increment = list(range(source_x, Nx)) + list(range(0, sink_x+1))
        y_to_increment = list(range(source_y, Ny)) + list(range(0, sink_y+1))
        ret = []
        for x in x_to_increment:
            for y in y_to_increment:
                ret.append((x, y))
        return tuple(ret)  # x_to_increment, y_to_increment


# def crange(start, end, modulo):
#     # print('aag')
#     # import pdb; pdb.set_trace()

#     if start > end:
#         while start < modulo:
#             yield start
#             start += 1
#         start = 0

#     while start <= end:
#         yield start
#         start += 1

class BoundingBoxPlacer(Annealer):
    # pass extra data (the distance matrix) into the constructor

    ''' going from [[0 for x in range( self.Ny )] for x in range( self.Nx )] to [[0] * self.Ny ] * self.Nx gave
    savings from 5.2s to 3.8s in energy().  then 2.27 by memoizing dataflow graph. apparently, 0.203 for not resetting net_congestion every time?
    down to 0.1 memoizing torus

    This gave me the same result as above for one, would be good to experiment.
    I got C=2 with this but only C=3 with above on this benchmark: python3 mocarabe.py -dfg hls/int_gaussian -II 1 -C 1 --place_time 1 --sched_method ILP -T 1 -iod 1 -ard 1 --unroll 3

    '''

    def __init__(self, state, dataflow_hypergraph, partitioned_netlist, Nx, Ny, dfg_v_to_partition_id, viz_placement_dir=False):  # TODO GET RID OF NX NY
        super(BoundingBoxPlacer, self).__init__(state)

        self.dataflow_hypergraph = dataflow_hypergraph
        self.partitioned_netlist = partitioned_netlist
        self.Nx = Nx
        self.Ny = Ny
        self.dfg_v_to_partition_id = dfg_v_to_partition_id
        self.viz_placement_dir = viz_placement_dir
        self.update_count = lambda c=itertools.count(): next(c)

        self.memoized_source_pe_and_dest_partitions = []
        # memoize tail(source)/head(dest) nodes, as ints.
        for hyperedge_id in list(self.dataflow_hypergraph.ordered_hyperedge_id_iterator()):
            net = self.dataflow_hypergraph.get_hyperedge_attributes(
                hyperedge_id)
            source = net['tail'][0]
            source_pe = self.dfg_v_to_partition_id[int(source)]
            for sink in net['head']:
                self.memoized_source_pe_and_dest_partitions.append(
                    (source_pe, self.dfg_v_to_partition_id[int(sink)]))

        self.memoized_Nx_toroidal_range = [
            [0 for a in range(Nx)] for b in range(Nx)]
        for source in range(Nx):
            for dest in range(Nx):
                self.memoized_Nx_toroidal_range[source][dest] = toroidal_range(
                    source, dest, Nx)
        self.memoized_Ny_toroidal_range = [
            [0 for a in range(Ny)] for b in range(Ny)]

        for source in range(Ny):
            for dest in range(Ny):
                self.memoized_Ny_toroidal_range[source][dest] = toroidal_range(
                    source, dest, Ny)
        self.memoized_bbox_generator = [
            [0 for a in range(Nx*Ny)] for b in range(Nx*Ny)]
        self.memoized_congestion = [
            [0 for a in range(Nx*Ny)] for b in range(Nx*Ny)]
        for source in range(Nx*Ny):
            for dest in range(Nx*Ny):
                self.memoized_bbox_generator[source][dest] = bbox_generator(
                    source, dest, Nx, Ny)

                self.memoized_congestion[source][dest] = len(
                    bbox_generator(source, dest, Nx, Ny))

    def move(self):
        a = int((len(self.state)-1) * random.random())
        b = int((len(self.state)-1) * random.random())

        self.state[a], self.state[b] = self.state[b], self.state[a]

        return

    def energy(self):

        # congestion = [[0] * self.Ny ] * self.Nx
        congestion = 0
        for source_partition, dest_partition in self.memoized_source_pe_and_dest_partitions:
            congestion += self.memoized_congestion[self.state[source_partition]
                                                   ][self.state[dest_partition]]
        return congestion
        #     xy_to_increment = self.memoized_bbox_generator[self.state[source_partition]][self.state[dest_partition]]

        #     for x,y in [*xy_to_increment]:
        #         congestion[x][y] += 1

        # e=0
        # for x in range( self.Nx ):
        #     for y in range( self.Ny ):
        #         e += congestion[x][y]

        # return e
