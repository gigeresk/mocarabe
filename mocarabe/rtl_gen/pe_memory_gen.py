import itertools
import copy

import numpy as np


def torus_min_distance_xy(sourcexy, sinkxy, Nx, Ny) -> tuple:
    source_x = sourcexy % Nx
    source_y = sourcexy // Nx
    sink_x = sinkxy % Nx
    sink_y = sinkxy // Nx

    # assert( source_x < Nx )
    # assert( sink_x < Nx )
    # assert( source_y < Ny )
    # assert( sink_y < Ny )

    if (source_x <= sink_x and source_y <= sink_y):
        '''
        --------------
        |  / >> snk  |
        |  ^         |
        | src        |
        --------------
        '''
        # no rollover
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
        # \n
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
        return ((Nx - source_x + sink_x), (Ny + - source_y + sink_y))


def get_net_path_nodes(dataflow_graph, resource_graph, device, h, v, enter, exit_) -> list:
    net_paths = []
    # for every net
    for net_id, hyperedge_id in enumerate(dataflow_graph.ordered_hyperedge_id_iterator()):
        p = net_id
        net_path = []

        # pe_out
        for x in range(device.Nx):
            for y in range(device.Ny):
                for c in range(device.physical_channels):
                    for t in range(device.schedule_length):
                        if enter[x][y][c][p][t] == 1:
                            net_path.append(resource_graph.pe[(x, y)])

                            for t in range(device.schedule_length):
                                net_path.append(
                                    resource_graph.pe_out[(x, y, t)])
                                for io_o in range(device.IO_O):
                                    # will result in too many but thats ok
                                    net_path.append(
                                        resource_graph.pe_out_port[(x, y, io_o, t)])
                                net_path.append(
                                    resource_graph.pe_out_switch[(x, y, c, t)])

        # routing
        for x in range(device.Nx):
            for y in range(device.Ny):
                for t in range(device.schedule_length):
                    for c in range(device.physical_channels):
                        if h[x][y][c][p][t] == 1:
                            net_path.append(resource_graph.h_noc[(x, y, c, t)])
                        if v[x][y][c][p][t] == 1:
                            net_path.append(resource_graph.v_noc[(x, y, c, t)])

        # pe_in
        for x in range(device.Nx):
            for y in range(device.Ny):
                for t in range(device.schedule_length):
                    for c in range(device.physical_channels):
                        if exit_[x][y][c][p][t] == 1:
                            net_path.append(resource_graph.pe[(x, y)])

                            for t in range(device.schedule_length):
                                net_path.append(
                                    resource_graph.pe_in[(x, y, t)])
                                for io_i in range(device.IO_I):
                                    # will result in too many but thats ok
                                    net_path.append(
                                        resource_graph.pe_in_port[(x, y, io_i, t)])
                                net_path.append(
                                    resource_graph.pe_in_switch[(x, y, c, t)])
        net_paths.append(net_path)

    return net_paths


def cycle_for_pe_op(head_pe_xy, net_id, variable, C, T) -> int:

    for c in range(C):
        for t in range(T):
            try:
                if variable[head_pe_xy[0]][head_pe_xy[1]][c][net_id][t] == 1:
                    return t
                if variable[head_pe_xy[0]][head_pe_xy[1]][c][net_id][t] == 1.0:
                    return t
            except:
                continue
    assert False, "cycle_for_pe_op(): Invalid solution"

'''
Recursive function to generate global timing schedule
'''


def generate_unadjusted_global_timing(head_node, this_edge, global_node_execute_cycle, global_node_enter_cycle, node_and_edge_port, edge_and_fanout_node_cycles_on_noc, enter, exit_, placement, dataflow_graph, device):
    head_pe_xy = placement[head_node]

    # get tail
    tail_node = dataflow_graph.get_hyperedge_attribute(this_edge, 'tail')[0]
    tail_pe_xy = placement[tail_node]
    net_id = int(this_edge[1:])-1

    tail_node_noc_enter_cycle_modulo = cycle_for_pe_op(
        tail_pe_xy, net_id, enter, device.physical_channels, device.II)

    ''' TIME SPENT ON NOC '''
    cycles_spent_on_noc_by_head_edge = 0
    earliest_noc_enter_cycle_for_tail_node = 0

    # calculate how many cycles this will be on the routing fabric for
    head_xy = head_pe_xy[0] + device.Nx*head_pe_xy[1]
    tail_xy = tail_pe_xy[0] + device.Nx*tail_pe_xy[1]
    x_diff, y_diff = torus_min_distance_xy(
        tail_xy, head_xy, device.Nx, device.Ny)

    cycles_spent_on_noc_by_head_edge += (x_diff +
                                         y_diff) * (device.noc_pipelining_stages+1)

    edge_and_fanout_node_cycles_on_noc[int(
        this_edge[1:])-1][head_node] = cycles_spent_on_noc_by_head_edge
    earliest_noc_enter_cycle_for_tail_node = global_node_execute_cycle[
        head_node] - cycles_spent_on_noc_by_head_edge - 7

    ''' Align cycle with what the schedule found '''
    while ((earliest_noc_enter_cycle_for_tail_node) % device.II) != tail_node_noc_enter_cycle_modulo:
        earliest_noc_enter_cycle_for_tail_node -= 1

    if tail_node in global_node_enter_cycle:
        # this node fans out to more than one op: it has to leave as early as possible.
        global_node_enter_cycle[tail_node] = min(
            earliest_noc_enter_cycle_for_tail_node, global_node_enter_cycle[tail_node])
    else:
        global_node_enter_cycle[tail_node] = earliest_noc_enter_cycle_for_tail_node

    global_node_execute_cycle[tail_node] = global_node_enter_cycle[tail_node] - \
        device.pe_pipelining_stages

    def channel_count(c=itertools.count(0)): return next(c)
    predecessor_hedges = dataflow_graph.get_predecessors(tail_node)

    for predecessor_hedge in predecessor_hedges:
        node_and_edge_port[(tail_node, predecessor_hedge)] = channel_count()
        global_node_execute_cycle, global_node_enter_cycle, node_and_edge_port, edge_and_fanout_node_cycles_on_noc = generate_unadjusted_global_timing(
            tail_node, predecessor_hedge, global_node_execute_cycle, global_node_enter_cycle, node_and_edge_port, edge_and_fanout_node_cycles_on_noc, enter, exit_, placement, dataflow_graph, device)  # enter, C, T won't change

    return global_node_execute_cycle, global_node_enter_cycle, node_and_edge_port, edge_and_fanout_node_cycles_on_noc


def adjust_global_timing(global_node_execute_cycle, global_node_enter_cycle, device):
    most_negative_time = 0
    startup_latency = 0

    for it in global_node_execute_cycle.values():
        most_negative_time = min(most_negative_time, it)

    while most_negative_time % device.II != 0:  # align the schedule with II
        most_negative_time -= 1
        startup_latency += 1

    for k, v in global_node_execute_cycle.items():
        global_node_execute_cycle[k] = v - most_negative_time
    for k, v in global_node_enter_cycle.items():
        global_node_enter_cycle[k] = v - most_negative_time
    latency = -most_negative_time

    return global_node_execute_cycle, global_node_enter_cycle, latency, startup_latency


def get_exit_channel_and_cycle(exit_, x, y, net_id, C, T):
    for c in range(C):
        for t in range(T):
            if exit_[x][y][c][net_id][t] == 1:
                return c, t


def generate_op_addresses_and_op_port_select(device, NUM_OPERANDS, T, exit_, dataflow_graph, global_node_execute_cycle, global_node_enter_cycle, placement, node_and_edge_port, edge_and_fanout_node_cycles_on_noc):

    Nx = device.Nx
    Ny = device.Ny
    IO_I = device.IO_I
    C = device.physical_channels
    op_addresses = np.zeros((Nx, Ny, NUM_OPERANDS, T), dtype=int)
    op_port_select = np.zeros((Nx, Ny, NUM_OPERANDS, T), dtype=int)
    sibling_operands = dataflow_graph.get_sibling_operands()

    samecycle_hedges = np.ndarray((Nx, Ny, T), dtype=object)
    for x in range(Nx):
        for y in range(Ny):
            for t in range(T):
                samecycle_hedges[x][y][t] = dict()

    pe_in_events = []  # (arrival_time, port, head_pe_xy, tail_node)

    edge_each_fanout_write_into_srl_time = [
        0] * len(dataflow_graph.ordered_hyperedge_id_list())

    for ix in range(len(dataflow_graph.ordered_hyperedge_id_list())):
        edge_each_fanout_write_into_srl_time[ix] = dict()

    for hyperedge_id in dataflow_graph.ordered_hyperedge_id_iterator():
        tail_node = dataflow_graph.get_hyperedge_attributes(hyperedge_id)[
            'tail'][0]
        tail_label = dataflow_graph.get_node_attributes(tail_node)['label']
        tail_pe_xy = placement[tail_node]

        # fanout
        for head_node in dataflow_graph.get_hyperedge_attribute(hyperedge_id, 'head'):
            head_pe_xy = placement[head_node]

            arrival_time = global_node_enter_cycle[tail_node] + \
                edge_and_fanout_node_cycles_on_noc[int(
                    hyperedge_id[1:])-1][head_node]
            edge_each_fanout_write_into_srl_time[int(
                hyperedge_id[1:])-1][head_node] = arrival_time + 1
            write_into_srl_time = edge_each_fanout_write_into_srl_time[int(
                hyperedge_id[1:])-1][head_node]

            cycles_on_noc = edge_and_fanout_node_cycles_on_noc[int(
                hyperedge_id[1:])-1][head_node]
            hops = cycles_on_noc // (device.noc_pipelining_stages + 1)

            execute_time_for_this_op = global_node_execute_cycle[head_node]
            load_time = (execute_time_for_this_op - 2) % T

            try:
                this_node_and_edge_port = node_and_edge_port[(
                    head_node, hyperedge_id)]
            except:
                a = 1  # print("SKIPPED\n\n")

            c, t = get_exit_channel_and_cycle(
                exit_, head_pe_xy[0], head_pe_xy[1], int(hyperedge_id[1:])-1, C, T)
            t_mux = t % T
            possible_ports = [*range(IO_I)]  # ports

            # if a = b + c, b and c can't use the same PE port
            for sibling_hedge, port in sibling_operands[int(head_node)].items():
                if sibling_hedge == hyperedge_id:
                    continue
                if port in possible_ports:
                    possible_ports.remove(port)

            # can't use the same port as another
            for samecycle_hedge, port in samecycle_hedges[head_pe_xy[0]][head_pe_xy[1]][t_mux].items():
                if samecycle_hedge == hyperedge_id:
                    continue
                if port in possible_ports:
                    possible_ports.remove(port)  # port in use in PE

            assert (len(possible_ports) >
                    0), "There must be some ports left to choose from"

            # Choose first available port
            port = possible_ports[0]

            sibling_operands[int(head_node)][hyperedge_id] = port
            samecycle_hedges[head_pe_xy[0]
                             ][head_pe_xy[1]][t_mux][hyperedge_id] = port

            op_port_select[head_pe_xy[0]][head_pe_xy[1]][port][t_mux] = c

            A_val = execute_time_for_this_op - arrival_time - 5
            op_addresses[head_pe_xy[0]][head_pe_xy[1]
                                        ][port][load_time] = A_val

            assert (op_addresses[head_pe_xy[0]]
                    [head_pe_xy[1]][port][load_time] >= 0)

            pe_in_events.append((arrival_time, port, head_pe_xy, tail_node))

    return op_addresses, op_port_select, pe_in_events


''' Given values for all input nodes and a DFG, return a dict with every node's value'''


def get_node_values(input_values, dataflow_graph):
    # note that we assume 2-input operations

    known_node_values = copy.deepcopy(input_values)

    unknown_nodes = dataflow_graph.ordered_node_id_list()
    for node, value in known_node_values.items():
        unknown_nodes.remove(node)

    while len(unknown_nodes) > 0:
        for unknown_node in unknown_nodes:
            parent_nodes = dataflow_graph.get_parent_nodes(unknown_node)

            both_parents_are_known = all(
                [x in known_node_values.keys() for x in parent_nodes])

            if both_parents_are_known and len(parent_nodes) > 0:

                head_label = dataflow_graph.get_node_attribute(
                    unknown_node, 'label')

                if head_label == '*':
                    known_node_values[unknown_node] = known_node_values[parent_nodes[0]
                                                                        ] * known_node_values[parent_nodes[1]]
                elif head_label == '+':
                    known_node_values[unknown_node] = known_node_values[parent_nodes[0]
                                                                        ] + known_node_values[parent_nodes[1]]
                else:
                    assert (
                        True), f"Unsupported operand {head_label}.  Please add support"

                unknown_nodes.remove(unknown_node)

    return known_node_values


def generate_and_write_pe_memories(proj_dir, resource_graph, net_paths, dataflow_graph, placement_result, enter, exit_, NUM_OPERANDS, IO_I, II, device):

    global_node_enter_cycle = dict()
    node_and_edge_port = dict()
    edge_and_fanout_node_cycles_on_noc = [
        0] * len(dataflow_graph.ordered_hyperedge_id_list())

    for ix in range(len(dataflow_graph.ordered_hyperedge_id_list())):
        edge_and_fanout_node_cycles_on_noc[ix] = dict()

    ''' Start generate_unadjusted_global_timing'''

    leaf_nodes = dataflow_graph.get_leaf_nodes()

    global_node_execute_cycle = dict()

    for leaf_node in leaf_nodes:
        leaf_node_pe_xy = placement_result[leaf_node]

        leaf_edges = dataflow_graph.node_is_head_for(leaf_node)
        for leaf_edge in leaf_edges:
            # leaf node exit output PE when the schedule allows it and after pipelining
            leaf_exit_noc_cycle = cycle_for_pe_op(leaf_node_pe_xy, int(
                leaf_edge[1:])-1, exit_, device.physical_channels, device.II)

            global_node_execute_cycle[leaf_node] = leaf_exit_noc_cycle - \
                device.pe_pipelining_stages
            global_node_execute_cycle, global_node_enter_cycle, node_and_edge_port, edge_and_fanout_node_cycles_on_noc = generate_unadjusted_global_timing(
                leaf_node, leaf_edge, global_node_execute_cycle, global_node_enter_cycle, node_and_edge_port, edge_and_fanout_node_cycles_on_noc, enter, exit_, placement_result, dataflow_graph, device)

    ''' Adjust all the timing according to most_negative_time'''
    global_node_execute_cycle, global_node_enter_cycle, latency, startup_latency = adjust_global_timing(
        global_node_execute_cycle, global_node_enter_cycle, device)

    ''' What we're really after '''
    # edge_each_fanout_write_into_srl_time does not really have to be returned
    op_addresses, op_port_select, pe_in_events = generate_op_addresses_and_op_port_select(
        device, NUM_OPERANDS, device.T, exit_, dataflow_graph, global_node_execute_cycle, global_node_enter_cycle, placement_result, node_and_edge_port, edge_and_fanout_node_cycles_on_noc)

    for operand in range(NUM_OPERANDS):
        for x in range(device.Nx):
            for y in range(device.Ny):
                string = ''
                for t in range(device.T):
                    string += hex(op_addresses[x][y][operand][t])[2:] + "\n"
                this_file = open(
                    proj_dir + f'/rtl/op{operand+1}_addr_memory_x{x}_y{y}.dat', "w+")
                this_file.write(string)
                this_file.close()

    for operand in range(NUM_OPERANDS):
        for x in range(device.Nx):
            for y in range(device.Ny):
                string = ''
                for t in range(device.T):
                    string += bin(op_port_select[x][y][operand][t])[2:] + "\n"
                this_file = open(
                    proj_dir + f'/rtl/mux{2}_x{x}_y{y}_sel_mem{operand}.dat', "w+")
                this_file.write(string)
                this_file.close()

    # invert global_node_enter_cycle
    enter_noc_cycle2node = dict()
    for k, cycle in global_node_enter_cycle.items():

        if cycle in enter_noc_cycle2node:
            enter_noc_cycle2node[cycle].append(k)
        else:
            enter_noc_cycle2node[cycle] = [k]

    # invert global_node_exit_cycle
    execute_cycle2node = dict()
    for k, cycle in global_node_execute_cycle.items():

        if cycle in execute_cycle2node:
            execute_cycle2node[cycle].append(k)
        else:
            execute_cycle2node[cycle] = [k]

    # assert_values
    root_node_values = {}
    for input_node in dataflow_graph.get_all_root_nodes():
        x, y = placement_result[input_node]
        root_node_values[input_node] = global_node_execute_cycle[input_node] + \
            100*(x + y*device.Nx)  # to prevent 0

    assert_values = get_node_values(root_node_values, dataflow_graph)

    # Second-iteration expected values: each root input shifts by II each period
    II = device.II
    root_node_values_2nd = {node: val + II for node, val in root_node_values.items()}
    assert_values_2nd = get_node_values(root_node_values_2nd, dataflow_graph)

    Nx = resource_graph.Nx

    # Collect all assertion events as (cycle, signal_expr, expected, label)
    events = []

    # First iteration: pe_out at node's NoC-enter cycle
    for cycle, nodes in enter_noc_cycle2node.items():
        for node in nodes:
            x, y = placement_result[node]
            events.append((cycle,
                           f'pe_out[{x} + {Nx}*{y}]',
                           assert_values[node],
                           f'node {node} iter1'))

    # Second iteration: same PEs II cycles later, with next period's data
    for cycle, nodes in enter_noc_cycle2node.items():
        for node in nodes:
            x, y = placement_result[node]
            events.append((cycle + II,
                           f'pe_out[{x} + {Nx}*{y}]',
                           assert_values_2nd[node],
                           f'node {node} iter2'))

    # Operand arrival: pe_in{port} at each head PE when the value is visible at the mux output.
    # arrival_time is when the data reaches the last NoC switch; +2 for the o_to_pe pipeline
    # (o_to_pe_r + o_to_pe_pipe), so the mux output is stable at sim time arrival_time+3
    # (mux_to_pe-after-g(arrival+2), which is what op_reg will capture).
    for arrival_time, port, head_pe_xy, tail_node in pe_in_events:
        hx, hy = head_pe_xy
        events.append((arrival_time + 3,
                       f'pe_in{port}[{hx} + {Nx}*{hy}]',
                       assert_values[tail_node],
                       f'operand to PE({hx},{hy}) port {port} from node {tail_node}'))

    events.sort(key=lambda e: e[0])
    assert_count = len(events)

    asserts_string = ""
    last_cycle = 0
    for cycle, grp in itertools.groupby(events, key=lambda e: e[0]):
        step = cycle - last_cycle
        asserts_string += f"        #{step} //cycle {cycle}\n"
        for _, signal, expected, label in grp:
            asserts_string += f'        assert({signal} == {expected}) $display("OK: {signal}=={expected} ({label})");\n'
            asserts_string += f'        else begin fail_count = fail_count + 1; $display("Assert error: {signal}==%0d @{cycle}, should be {expected} ({label})", {signal}); end\n'
        last_cycle = cycle

    asserts_string += f'        if (fail_count == 0)\n'
    asserts_string += f'            $display("\\n=== PASS: all {assert_count} assertions passed ===");\n'
    asserts_string += f'        else\n'
    asserts_string += f'            $display("\\n=== FAIL: %0d of {assert_count} assertions failed ===", fail_count);\n'
    asserts_string += "        #10\n"
    asserts_string += "        $finish;\n"

    return op_addresses, op_port_select, asserts_string, latency
