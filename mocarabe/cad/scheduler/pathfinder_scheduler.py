import ast
import heapq
import os
import sys
import random

import networkx as nx

from mocarabe.device import Device
from mocarabe.resource_graph import ResourceGraph
from mocarabe.resource_type import ResourceType
from .scheduled_netlist import ScheduledNetlist
from .scheduled_net import ScheduledNet


class UnroutableError(Exception):
    pass


class Connection:
    lastId = 0

    # for pathfinder_ts input
    def __init__(self, source_xy, fanouts_xy, hyperedge_id):
        self.source_xy = source_xy
        self.fanouts_xy = fanouts_xy
        self.time_slot = 0
        self.id = Connection.lastId
        Connection.lastId += 1  # kind of weird

        self.locked = False

        self.starting_time = 0
        self.net_path = []  # * num_of_nets

        self.hyperedge_id = hyperedge_id  # for dataflow graph

    def lock(self):
        print(f'Locking connection {self.id}')
        self.locked = True

    def add_to_path(self, node):
        self.net_path.append(node)

    def rip_up(self):
        if self.net_path != []:
            # source = self.net_path[0]
            self.net_path = []

    def set_start_time(self, start_time):
        self.starting_time = start_time

    def __getitem__(self, ix):
        return self.net_path[ix]

    @staticmethod
    def reset_net_ids():
        Connection.lastId = 0


class MinHeap:
    def __init__(self, init_cost, init_node):
        self.__expansion_list = [(init_cost, init_node)]
        self.__expansion_list_node_set = {init_node}
        self.__expansion_list_length = 1

    def push(self, node, cost):
        # for cost_and_node in self.__expansion_list:
        #     if node == cost_and_node[1]:
        #         # print('already in expansion list')
        #         return False
        if node in self.__expansion_list_node_set:
            return False

        heapq.heappush(self.__expansion_list, (cost, node))
        self.__expansion_list_node_set.add(node)
        self.__expansion_list_length += 1
        return True

    def pop(self):
        if self.length() > 0:
            res = heapq.heappop(self.__expansion_list)
            self.__expansion_list_node_set.remove(res[1])  # I hope this works?
            self.__expansion_list_length -= 1
            return res
        else:
            return -1

    def length(self):
        return self.__expansion_list_length

    def get(self):
        return self.__expansion_list


class Pathfinder:

    def __init__(self, resource_graph, connections, MAX_ITER_pf=20, MAX_ITER_tp=10, VERBOSE=False):
        self.G = resource_graph

        # self.nodes_used_by_net = [[]] * resource_graph.number_of_nodes()

        self.history_ts = [0] * resource_graph.number_of_nodes()

        self.connections = connections

        self.congestion_ts = [0] * resource_graph.number_of_nodes()

        self.G_copy = self.G.copy()
        self.G_reverse = self.G_copy.reverse(False)

        self.MAX_ITER_pf = MAX_ITER_pf  # max iter in a pathfinder_ts loop
        # max iter in a traffic_path loop (esp. for T=1)
        self.MAX_ITER_tp = MAX_ITER_tp
        self.VERBOSE = VERBOSE

    def shared_channel_slot_pairs_exist(self):
        # print("TODO: cleanup here")
        ''' It's quite ok to share PEs, and it doesn't count as a contested resource.
        However, don't want to mess with the algorithm by having zero-cost nodes everywhere,
        so we just reset the congestion each iteration'''

        for pe_nodes in self.G.pe_nodes:
            self.congestion_ts[pe_nodes] = 0

        for pe_in_nodes in self.G.pe_in_nodes:
            self.congestion_ts[pe_in_nodes] = 0
        for pe_in_port_node in self.G.pe_in_port_nodes:
            self.congestion_ts[pe_in_port_node] = 0
        # print('congestion test!')
        # for node, node_congestion in enumerate(self.congestion_ts):
        #     if node_congestion > 1:
        #         print(f'{self.G.node_to_resource(node)} is congested')
        # print('')
        if all(node_congestion < 2 for node_congestion in self.congestion_ts):
            # print('bad')
            return False
        else:
            # print('good')
            return True

    def shared_channel_slot_pairs_exist_for_connection(self, routed_path):
        # print("TODO: cleanup here")
        ''' It's quite ok to share PEs, and it doesn't count as a contested resource.
        However, don't want to mess with the algorithm by having zero-cost nodes everywhere,
        so we just reset the congestion each iteration'''

        for pe_nodes in self.G.pe_nodes:
            self.congestion_ts[pe_nodes] = 0

        for pe_in_nodes in self.G.pe_in_nodes:
            self.congestion_ts[pe_in_nodes] = 0
        # TODO RECONSIDER>>>
        for pe_in_port_node in self.G.pe_in_port_nodes:
            self.congestion_ts[pe_in_port_node] = 0

        # print('congestion test!')
        for node, node_congestion in enumerate(self.congestion_ts):
            if node not in routed_path:
                continue  # specific to this net
            if node_congestion > 1:
                print(
                    f'{self.G.node_to_resource(node)} is congested ({node_congestion})')
                return True
        return False
        # print('')
        # if all(node_congestion < 2 for node_congestion in self.congestion_ts):
        #     print('bad')
        #     return False
        # else:
        #     print('good')
        #     return True

    def cost_of_using_node(self, node):
        p_fac = 1.2
        h_fac = 0.2

        cost = (1 + self.congestion_ts[node] * p_fac) * \
            (1 + self.history_ts[node] * h_fac)

        return cost

    def backtrace(self, lowest_cost_nodes, source_node, dest_node):
        # in: reversed resource graph and expansion_list
        # print(f'source_node: {self.G.node_to_resource(source_node)}')
        reverse_graph = self.G_reverse
        # expansion_list_nodes = expansion_list.list_nodes_only()
        # lowest_cost_nodes.append(source_node)
        # lowest_cost_nodes.append(dest_node)
        # expansion_list: only caare about the second item in every node
        subgraph = reverse_graph.subgraph(lowest_cost_nodes)
        # TODO improve...

        backtraced_path = nx.shortest_path(subgraph, dest_node, source_node)

        # backtraced_path = [dest_node]
        # backtraced_node = dest_node
        # while source_node not in backtraced_path:
        #     backtrace_successors = list(reverse_graph.successors( backtraced_node ))

        #     tentative_successors = list(set(backtrace_successors) & set(expansion_list_nodes))
        #     print(f'tentative_successors: {tentative_successors}')
        #     chosen_successor = tentative_successors[0] # no smarter choice made

        #     backtraced_path.append( chosen_successor )
        #     backtraced_node = chosen_successor

        # for backtraced_node in backtraced_path:
        # add to path
        # print( self.G.node_to_resource(backtraced_node) )
        # succ = list( self.G.successors(backtraced_node) )
        # print(succ)

        return backtraced_path

    # def all_destinations_found( )
    def pathfinder_ts(self, starting_slot, list_of_connections):
        '''# Data: List of connections (source, destination, starting time slot)
        # Result: List of routing paths (S) for each connection of channel, time slot pairs'''

        list_of_connections = self.connections  # TODO improve

        assert (type(list_of_connections) == list)
        if len(list_of_connections) > 0:
            assert (type(list_of_connections[0] == Connection))
        else:
            return

        iteration_count = 0

        while (self.shared_channel_slot_pairs_exist() and iteration_count < self.MAX_ITER_pf) or iteration_count == 0:
            if self.VERBOSE:
                print(f'iteration {iteration_count}')

            for connection in list_of_connections:

                starting_slot = (random.randint(0, self.G.T)) % self.G.T

                if connection.locked:
                    continue
                # print(f'listofconnections length: {len(list_of_connections)}')
                if self.VERBOSE:
                    print(
                        f'Processing connection {connection.id} at starting slot {starting_slot}')

                # RIP UP: remove from congestion cost
                if connection.net_path != []:
                    # print('removing nets from congestion')
                    for node in connection.net_path:
                        self.congestion_ts[node] -= 1

                connection.rip_up()
                connection.set_start_time(starting_slot)

                # Start time is random.  Only has an effect when resource sharing (II>1)
                # Unlike traditional pathfinder_ts, we can have tight configurations where nothing ever gets locked.
                source = self.G.pe_out[(
                    connection.source_xy[0], connection.source_xy[1], starting_slot)]

                sink_nodes = []
                for sink in connection.fanouts_xy:
                    assert (sink in self.G.pe.keys())
                    sink_node = self.G.pe[(sink[0], sink[1])]  # removed i_slot
                    sink_nodes.append(sink_node)

                path_cost_Ci = [0] * self.G.number_of_nodes()
                expansion_list = MinHeap(0, source)
                shortest_path = []
                for sink in sink_nodes:  # "LOOP UNTIL ALL SINKS HAVE BEEN FOUND"
                    sink_shortest_path = []
                    sink_xy = self.G.getxy(sink)
                    # LOOP UNTIL NEW SINK (ONLY SINK, IN OUR CASE) IS FOUND
                    # while sink not in expansion_list.list_nodes_only(): # is too slow

                    sink_switches = set()
                    for c in range(self.G.physical_channels):
                        for t in range(self.G.T):
                            sink_switches.add(
                                self.G.pe_in_switch[(sink_xy[0], sink_xy[1], c, t)])

                    while not any(i in sink_switches for i in sink_shortest_path):
                        node_m = expansion_list.pop()  # lowest cost nodes
                        if node_m == -1:
                            print('not good, empty expansion_list??')
                            import pdb
                            pdb.set_trace()
                        cost, node_m = node_m  # unpack...

                        # LOOP OVER FANOUTS OF M
                        for fanout_n in self.G.successors(node_m):
                            # TODO: to match the newer paper more closely, possibly only allow sane moves
                            # e.g. nothing that requires an UNNECESSARY torus spillover or unrelated PE entrance
                            # print("fanout of node_m!")

                            # want to ensure that we don't wander into other PEs
                            # print(f'{self.G.node_to_resource(node_m)} to {self.G.node_to_resource(fanout_n)}' )
                            fanout_n_attr = self.G.node_attributes_params[fanout_n]
                            if connection.id == 6 and self.G.node_attributes_type[fanout_n] == ResourceType.PE_OUT_SWITCH:
                                print(
                                    f"PROCESSING C={fanout_n_attr[2]} SWITCH (fanout_n)")

                            if (fanout_n not in self.G.pe_in_nodes and fanout_n not in self.G.pe_nodes) or (fanout_n_attr[0], fanout_n_attr[1]) == sink_xy:
                                n_cost = self.cost_of_using_node(fanout_n)

                                # TODO check this out too...
                                pushed = expansion_list.push(
                                    fanout_n, n_cost + path_cost_Ci[node_m])
                                # print(f'pushed {self.G.node_to_resource(fanout_n)} at cost {n_cost + path_cost_Ci[node_m]}')
                                path_cost_Ci[fanout_n] = n_cost + \
                                    path_cost_Ci[node_m]
                                if pushed and connection.id == 6:
                                    print(
                                        f'pushing: {self.G.node_to_resource(fanout_n)} [{fanout_n}] at cost {path_cost_Ci[fanout_n]}')
                        # print(f'adding {self.G.node_to_resource(node_m)} to sink_shortest_path')
                        sink_shortest_path.append(node_m)

                        # self.net_paths.add_to_path( net_id=connection.id, node=node_m )
                        '''
                        # TODO fanout support
                        # while fanout n of node m at time slot (j+1) mod max_slot on shortest_path exist:
                            # add n to expansion_list at cost cn + Ci
                                # heapq.heappush( expansion_list, (cost, details) )

                        '''

                    shortest_path = shortest_path + sink_shortest_path
                    proper_switch = list(
                        set([i for i in shortest_path if i in sink_switches]))

                    shortest_path.append(proper_switch[0])
                    # i[1] in sink_switches for i in expansion_list._MinHeap__expansion_list
                    # print('was found')
                    # after a sink switch is found, add all successive nodes until PE
                    # If I understand, we have only added one pe in switch, so the shortest path will use this switch

                    # shortest_path = list(set(shortest_path))
                    for t in range(self.G.T):
                        for io_i in range(self.G.IO_I):
                            # pe_in_port (x,y,io_i,t)
                            shortest_path.append(
                                self.G.pe_in_port[(sink_xy[0], sink_xy[1], io_i, t)])
                        # pe_in (x,y,t)
                        shortest_path.append(
                            self.G.pe_in[(sink_xy[0], sink_xy[1], t)])
                        for io_o in range(self.G.IO_O):
                            shortest_path.append(self.G.pe_out_port[(
                                # TODO: questionable lol
                                connection.source_xy[0], connection.source_xy[1], io_o, t)])
                        for c in range(self.G.physical_channels):
                            shortest_path.append(self.G.pe_out_switch[(
                                connection.source_xy[0], connection.source_xy[1], c, t)])

                    # shortest_path = list(set(shortest_path))
                    shortest_path.append(self.G.pe[(sink_xy[0], sink_xy[1])])

                    # here, was sending in 'expansion list' to backtraced path
                    # the problem with that is that it includes too many dead-end nodes

                    if source not in shortest_path:
                        shortest_path.append(source)
                        # TODO not ideal but with multi-fanout, we restrict pe_out to previous pe_out...
                    if sink not in shortest_path:
                        import pdb
                        pdb.set_trace()

                    backtraced_path = []
                    try:
                        backtraced_path = self.backtrace(
                            shortest_path, source, sink)
                    except nx.exception.NetworkXNoPath:
                        print("Unable to find a backtraced path: there is a bug.")

                    backtraced_path.reverse()

                    # do not reserve PE?
                    for backtraced_node in backtraced_path:
                        # add to path, unless already on the path
                        # TODO: doesn't prioritize (i.e. give 0 cost) to already-used nodes
                        if backtraced_node not in connection.net_path:
                            connection.add_to_path(node=backtraced_node)
                            self.congestion_ts[backtraced_node] += 1
                            self.history_ts[backtraced_node] += 1

                    # According to McMurchie and Ebeling ('95), reset expansion_list to current path
                    expansion_list = MinHeap(0, 0)
                    expansion_list.pop()

                    '''VERY IMPORTANT:
                    If you change the # of gateway nodes above (Pe, Pe in, Pe in switch, etc.),
                    you also have to change things here (in # of gateway nodes we truncate from
                    the net_path with e.g. [2:-4]! Only the switch and the interconnect should be reused.
                    '''
                    '''
                    Possible optimizations:
                    1) only add non-PE (port/in/etc.) nodes to path other than sink switches.
                    that way, fewer heap queries (?)
                    2) Queue up sink switches if we come across one.  Add it to the list of dests to add to
                    path at the end, and remove it from the set of sink nodes (switch or otherwise).  This
                    is left ambiguous in the pathfinderts paper, slightly less ambiguous in the '95 paper

                    '''
                    for node_in_path in reversed(connection.net_path):
                        # This filtering could come at a big efficiency cost,
                        # but I think this could be optimized later on...
                        if node_in_path in self.G.pe_out_switch.values():
                            expansion_list.push(node_in_path, 0)
                        elif node_in_path in self.G.h_noc.values() or node_in_path in self.G.v_noc.values():
                            expansion_list.push(node_in_path, 0)

            iteration_count += 1

        return self.connections  # TODO unmake make this a member variable

    def perform_set_route(self, unlocked_connections, starting_slot):
        # Data: set of unlocked connections, starting slot j

        # Result: list of routing paths (S) with no (channel, slot) pair overlaps

        # Result: Set of connections with (channels, slot) pair overlaps
        routed_paths = self.pathfinder_ts(starting_slot, unlocked_connections)

        locked_connections = []
        # lock all connections with paths with no (channel, slot) pairs that overlap
        for routed_path in routed_paths:

            if routed_path not in unlocked_connections:
                continue
            # all(self.congestion_ts[node] < 2 for node in routed_path.net_path[0:-1] ): # exclude the resource, a PE
            if not self.shared_channel_slot_pairs_exist_for_connection(routed_path):
                routed_path.lock()
                locked_connections.append(routed_path)
                if routed_path in unlocked_connections:
                    unlocked_connections.remove(routed_path)

        for unlocked_connection in unlocked_connections:
            print(f'connection {unlocked_connection.id} is unlocked')

        return unlocked_connections

    def traffic_path(self, connections):
        # Data: nets, list of multi-fanout connections

        # try all starting time slots
        num_slots = self.G.T  # TODO improve this
        unrouted_set = connections.copy()

        num_iter = 0
        while num_iter < self.MAX_ITER_tp:
            for i in range(num_slots):
                # unrouted_set = all connections
                for connection in connections:
                    connection.time_slot = i

                for j in range(i, num_slots):
                    print(f'Running traffic path at i={i}, j={j}')
                    # starting_slot = (random.randint(0,self.G.T)) % self.G.T
                    starting_slot = j
                    print(f'starting_sllotot: {starting_slot}')
                    unrouted_set = self.perform_set_route(
                        unrouted_set, starting_slot)
                    # for unrouted in unrouted_set:
                    #     print(self.G.nodes_to_resources(unrouted.net_path))
                    # if no shared( channel, time slot) paths;
                    if unrouted_set == []:
                        return connections
            num_iter += 1
        if unrouted_set != []:
            print('Failed...')
            return False
        else:
            print('Did not fail..')
        return connections


def schedule(self, device, dataflow_mode, netlist, io_pes, boundingBoxEnabled, file_name, benchmark, solFilename, file_helper):
    if not os.path.exists('log'):
        print("Creating 'log' directory")
        os.makedirs('log')
    if not os.path.exists('results'):
        print("Creating 'results' directory")
        os.makedirs('results')

    routed_connections = False
    Connection.reset_net_ids()

    G = ResourceGraph()
    G.create(device)

    # pos_ = nx.get_node_attributes(G,'pos')
    # label_ = nx.get_node_attributes(G,'label')
    # nx.draw(G,pos_)
    # plt.show()
    connections = []
    for net in netlist:
        src = net[0]
        dests = net[1]
        destsxy = []
        for dest in dests:
            destsxy.append((dest[0], dest[1]))

        connections.append(Connection(
            (src[0], src[1]), destsxy, hyperedge_id=src[4]))
    print(f'C: {device.physical_channels}')
    # Seems like tp beyond 6 isn't very useful.
    pf = Pathfinder(G, connections, MAX_ITER_tp=10, MAX_ITER_pf=6)

    routed_connections = pf.traffic_path(connections)
    if routed_connections == False:
        raise UnroutableError(
            "Could not route at " + str(device.physical_channels) + " physical channels")

    # if routed_connections != False:
        # for connection in routed_connections:
        #     for node in connection:
        #         sys.stdout.write( G.node_to_resource( node )+ "\n")
        #     sys.stdout.write('\n')

    string = ""
    log_file = file_helper.log_file

    scheduled_netlist = ScheduledNetlist(G)

    if routed_connections != False:
        for connection in routed_connections:
            scheduled_net = ScheduledNet()
            for node in connection[0:-1]:
                string += G.node_to_old_style(node, connection.id)

                node_type = G.node_attributes_type[node]
                if node_type == ResourceType.PE_OUT_SWITCH:
                    scheduled_net.enter_noc = node
                if node_type == ResourceType.H_NOC:
                    scheduled_net.noc_hops.append(node)
                if node_type == ResourceType.V_NOC:
                    scheduled_net.noc_hops.append(node)
                if node_type == ResourceType.PE_IN_SWITCH:
                    scheduled_net.exit_noc.append(node)

                sys.stdout.write(G.node_to_old_style(node, connection.id))
            sys.stdout.write('\n')
            scheduled_netlist.append(scheduled_net)
        file_helper.schedule_filepath = f"{file_helper.schedule_dir}{file_helper.benchmark_name}-Nx{device.Nx}-Ny{device.Ny}-C{device.physical_channels}-P{len(connections)}-T{device.schedule_length}.sol"
        f = open(file_helper.schedule_filepath, "w")
        f.write(string)
        f.close()

        routed_connections = routed_connections

    return scheduled_netlist


if __name__ == "__main__":
    # TODO make sure this still works
    ''' This interface was provided to profile the pathfinder_ts implementation
    Generate a *net netlist using the main compiler frontend, then come back and run
    python3 src/pathfinder_scheduler/_pathfinder_ts.py --netlist proj/int_gaussian_--22-09-20-16.43.49/netlist/int_gaussian.net -Nx 6 -Ny 6 -C 1 -T 1
    Take note of the netlist's Nx, Ny.  Select an appropriate T, ideally equal to II.  Only one value of C will be attempted.

    Profile with

    python3 -m cProfile <src/pathfinder_scheduler... -C 1 -T 1>
    '''
    import argparse
    import sys
    from unipath import Path

    parser = argparse.ArgumentParser(description='Space-Time ILP Scheduler')
    parser.add_argument('--netlist', metavar='*net file', required=True,
                        type=str, help='path to *net file to run pathfinder directly')
    parser.add_argument('-C', metavar='channel count', required=True,
                        type=int, help='exact # of physical channels')
    parser.add_argument('-Nx', metavar='x-dimension of 2D chip',
                        required=True, type=int, help='the x-size of the network')
    parser.add_argument('-Ny', metavar='y-dimension of 2D chip',
                        required=True, type=int, help='the y-size of the network')
    parser.add_argument('-T', metavar='schedule length', required=True,
                        type=int, default=0, help='schedule length (optional upper bound)')
    args = parser.parse_args()

    file_name = args.netlist

    Nx = args.Nx
    Ny = args.Ny
    C = args.C
    T = args.T

    IO_I = 2
    IO_O = 1
    pe_pipelining_stages = 5
    noc_pipelining_stages = 2
    layout = ''
    # from pathfinder_scheduler import ResourceGraph
    device = Device(Nx, Ny, C, T, IO_I, IO_O, layout,
                    pe_pipelining_stages, noc_pipelining_stages)
    resource_graph = ResourceGraph()
    resource_graph.create(device)

    connections = []
    f = open(file_name, 'r')

    lines = f.read().splitlines()
    maxP = len(lines)+1  # number of nets = number of lines in the netlist file
    fanout = [0] * maxP
    src_x = [0] * maxP
    src_y = [0] * maxP
    for p, line in enumerate(lines):
        line = line.partition('#')[0]  # comments
        rawnet = ast.literal_eval(line)
        src = rawnet[0]
        dests = rawnet[1:]
        destsxy = []
        for dest in dests:
            destsxy.append((dest[0], dest[1]))
        connections.append(Connection(
            (src[0], src[1]), destsxy, hyperedge_id=src[4]))

    print('starting pf')
    pf = Pathfinder(resource_graph, connections, MAX_ITER_tp=6, MAX_ITER_pf=10)

    routed_connections = pf.traffic_path(connections)

    # pf.pathfinder_ts( 0, connections )

    if routed_connections == False:
        exit()

    string = ""
    for connection in routed_connections:
        for node in connection:
            string += resource_graph.node_to_old_style(node, connection.id)
            sys.stdout.write(
                resource_graph.node_to_old_style(node, connection.id))
        sys.stdout.write('\n')

    sched_dir = Path(file_name).parent.parent.child("schedule")

    f = open(
        f"{sched_dir}/pathfinder_Nx{Nx}-Ny{Ny}-C{C}-P{len(connections)}-T{T}.sol", "w")
    f.write(string)
    f.close()
