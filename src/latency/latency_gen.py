import itertools

import networkx as nx
import numpy as np

from resource_graph import ResourceGraph
from resource_type import ResourceType

def get_net_path_nodes( dataflow_graph, resource_graph, device, h, v, enter, exit_ ):
    net_paths = []
    # for every net
    for net_id, hyperedge_id in enumerate(dataflow_graph.ordered_hyperedge_id_iterator()):
        p = net_id
        net_path = []

        # pe_out
        for x in range( device.Nx ):
            for y in range( device.Ny ):
                for c in range( device.physical_channels ):
                    for t in range( device.schedule_length ):
                        if enter[x][y][c][p][t] == 1:
                            net_path.append( resource_graph.pe[(x,y)])

                            for t in range( device.schedule_length ):
                                net_path.append( resource_graph.pe_out[(x,y,t)])
                                for io_o in range( device.IO_O ):
                                    net_path.append( resource_graph.pe_out_port[(x,y,io_o,t)] ) # will result in too many but thats ok
                                net_path.append( resource_graph.pe_out_switch[(x,y,c,t)] )

        # routing
        for x in range( device.Nx ):
            for y in range( device.Ny ):
                for t in range( device.schedule_length ):
                    for c in range( device.physical_channels ):
                        if h[x][y][c][p][t] == 1:
                            net_path.append( resource_graph.h_noc[(x,y,c,t)] )
                        if v[x][y][c][p][t] == 1:
                            net_path.append( resource_graph.v_noc[(x,y,c,t)] )

        # pe_in
        for x in range( device.Nx ):
            for y in range( device.Ny ):
                for t in range( device.schedule_length ):
                    for c in range( device.physical_channels ):
                        if exit_[x][y][c][p][t] == 1:
                            net_path.append( resource_graph.pe[(x,y)])

                            for t in range( device.schedule_length ):
                                net_path.append( resource_graph.pe_in[(x,y,t)])
                                for io_i in range( device.IO_I ):
                                    net_path.append( resource_graph.pe_in_port[(x,y,io_i,t)] ) # will result in too many but thats ok
                                net_path.append( resource_graph.pe_in_switch[(x,y,c,t)] )
        net_paths.append( net_path )

    return net_paths

def cycle_for_pe_op( head_pe_xy, net_id, variable, C,T ):
    try:
        for c in range(C):
            for t in range(T):
                if variable[head_pe_xy[0]][head_pe_xy[1]][c][net_id][t] == 1:
                    return t
    except:
        import pdb; pdb.set_trace()
        raise Exception("Not in here TODO")

    return 0

def generate_unadjusted_global_timing(  head_node, this_edge, head_node_enter_noc_cycle, global_node_execute_cycle,global_node_enter_cycle,node_and_edge_port,edge_and_fanout_relative_travel_time,enter, exit_, C, T,placement,dataflow_graph,resource_graph,net_paths, PE_PIPELINE_NUM_STAGES, Nx,Ny, II, device ):
    # TODO make static.
    # head node, this_edge, head_node_enter_noc_cycle are essential (if not poorly named)
    # we're not using exit_ here interestingly-> only in the next part
    # enter, exit_, C, T do not change.

    SCHED_LEN = II
    LOAD_OPS = 2 # read from srl_inst_op1/srl_inst_op2 + op1_reg/op2_reg
    # NOC_PIPELINE_NUM_STAGES = device.noc_pipelining_stages # After leaving every switch
    # PE_PIPELINE_NUM_STAGES = 2 # After executing an operation
    PORT_TO_OPERAND_CYCLE = 0 # Muxes from each port to each operand FIFO
    OP_LOAD_CYCLE = 1 # Load from operand FIFO
    REGISTER_OPERAND_CYCLE = 1 # Registered operands


    head_pe_xy = placement[head_node]
    head_node_in_res_graph = resource_graph.pe[(head_pe_xy[0], head_pe_xy[1])]

    # get tail
    tail_node = dataflow_graph.get_hyperedge_attribute( this_edge, 'tail')[0]
    tail_pe_xy = placement[tail_node]
    net_id = int(this_edge[1:])-1

    tail_node_noc_enter_cycle_modulo = cycle_for_pe_op( tail_pe_xy, net_id, enter, C,T )

    ''' TIME SPENT ON NOC '''
    #TODO would like to be able to do this better...
    net_path = net_paths[net_id]
    subgraph = resource_graph.subgraph( net_path )
    tail_node_in_res_graph = resource_graph.pe[(tail_pe_xy[0], tail_pe_xy[1])]

    # fanout_path = ""
    # try:
    #     fanout_path = nx.shortest_path(subgraph, tail_node_in_res_graph, head_node_in_res_graph )
    # except:
    #     print(f'No path found from {resource_graph.node_to_resource(tail_node_in_res_graph)} to {resource_graph.node_to_resource(head_node_in_res_graph)}')
    #     print(f'Net path: {resource_graph.nodes_to_resources(net_path)}')
    #     # import pdb; pdb.set_trace()

    cycles_on_noc = 0
    curr_enter_cycle = 0
    if tail_pe_xy[0] == head_pe_xy[0] and tail_pe_xy[1] == head_pe_xy[1]: # self edge
        cycles_on_noc += device.noc_pipelining_stages + 1
        curr_enter_cycle = global_node_execute_cycle[head_node] - 1- cycles_on_noc - REGISTER_OPERAND_CYCLE - OP_LOAD_CYCLE
        edge_and_fanout_relative_travel_time[int(this_edge[1:])-1][head_node] = cycles_on_noc
    else:
        # not self edge
        # for node_in_fanout_path in fanout_path:
        x_diff = head_pe_xy[0] - tail_pe_xy[0] % Nx
        y_diff = head_pe_xy[1] - tail_pe_xy[1] % Ny
        cycles_on_noc += ( x_diff + y_diff ) * device.noc_pipelining_stages
            # node_in_fanout_path_type = resource_graph.node_attributes_type[ node_in_fanout_path ]
            # if node_in_fanout_path_type == ResourceType.H_NOC or node_in_fanout_path_type == ResourceType.V_NOC or node_in_fanout_path_type == ResourceType.PE_IN_PORT:
            #     cycles_on_noc += NOC_PIPELINE_NUM_STAGES + 1

        edge_and_fanout_relative_travel_time[int(this_edge[1:])-1][head_node] = cycles_on_noc

        curr_enter_cycle = global_node_execute_cycle[head_node] - LOAD_OPS- cycles_on_noc - REGISTER_OPERAND_CYCLE - OP_LOAD_CYCLE - PORT_TO_OPERAND_CYCLE
    ''' ADJUST TIMING ON TRAVEL TIME AND PROCESSING TIME '''
    # Align to modulo schedule
    while ((curr_enter_cycle) % SCHED_LEN) != tail_node_noc_enter_cycle_modulo: #TODO yucky
        # import pdb; pdb.set_trace()
        # print('uh')
        curr_enter_cycle -= 1

    # Adjust for both operands
    if tail_node in global_node_enter_cycle:
        global_node_enter_cycle[tail_node] = min( curr_enter_cycle, global_node_enter_cycle[tail_node] )
    else:
        global_node_enter_cycle[tail_node] = curr_enter_cycle

    global_node_execute_cycle[tail_node] = curr_enter_cycle - device.pe_pipelining_stages

    channel_count = lambda c=itertools.count(0): next(c)
    predecessor_hedges = dataflow_graph.get_predecessors( tail_node )
    # import pdb; pdb.set_trace()
    for predecessor_hedge in predecessor_hedges:
        node_and_edge_port[(tail_node, predecessor_hedge)] = channel_count()
        global_node_execute_cycle,global_node_enter_cycle,node_and_edge_port,edge_and_fanout_relative_travel_time = generate_unadjusted_global_timing( tail_node, predecessor_hedge, curr_enter_cycle,global_node_execute_cycle,global_node_enter_cycle,node_and_edge_port,edge_and_fanout_relative_travel_time, enter, exit_, C, T,placement,dataflow_graph,resource_graph,net_paths, PE_PIPELINE_NUM_STAGES, Nx,Ny,II, device ) # enter, C, T won't change

    if predecessor_hedges == set():
        # root node
        global_node_execute_cycle[tail_node] = global_node_enter_cycle[tail_node] - device.pe_pipelining_stages
        return global_node_execute_cycle,global_node_enter_cycle

    return global_node_execute_cycle,global_node_enter_cycle, node_and_edge_port,edge_and_fanout_relative_travel_time


def adjust_global_timing( global_node_execute_cycle,global_node_enter_cycle ):
    most_negative_time = 0

    for it in global_node_execute_cycle.values():
        most_negative_time = min( most_negative_time, it )
    for it in global_node_enter_cycle.values():
        most_negative_time = min( most_negative_time, it )

    if most_negative_time % 2 == 1: # if odd
        most_negative_time -= 1
    for k,v in global_node_execute_cycle.items():
        global_node_execute_cycle[k] = v - most_negative_time
    for k,v in global_node_enter_cycle.items():
        global_node_enter_cycle[k] = v - most_negative_time
    latency = -most_negative_time
    return global_node_execute_cycle, global_node_enter_cycle, latency

def get_critical_path_root_node( global_node_execute_cycle ):

    return min(global_node_execute_cycle, key=global_node_execute_cycle.get)

def get_node_values( input_values, dataflow_graph ):
    # inefficient but these graphs have all been small so far.

    # if type( input_values ) == int:
    #     input_values = 7
    node_values = {}

    leaf_node = dataflow_graph.get_leaf_node()[0]

    # add inputs
    input_nodes = dataflow_graph.get_all_root_nodes()

    for input_node in dataflow_graph.get_all_root_nodes():
        node_values[input_node] = input_values
    print(node_values)

    partial_results = {}

    while len(dataflow_graph.get_node_set()) != len(node_values):
        print(f"{len(dataflow_graph.get_node_set())} != {len(node_values)}" )
        for hyperedge_id in dataflow_graph.ordered_hyperedge_id_iterator():
            hyperedge = dataflow_graph.get_hyperedge_attributes( hyperedge_id )
            tail_id = hyperedge['tail'][0]

            if tail_id not in node_values: continue # node already computed

            heads = hyperedge['head']
            for head_id in heads:
                head_label = dataflow_graph.get_node_attribute( head_id, 'label' )

                if head_id not in partial_results:
                    partial_results[head_id] = [tail_id, node_values[tail_id]]
                elif head_id in partial_results and partial_results[head_id][0] != tail_id:
                    # already computed only the other half of the partial sum
                    if head_label == '*':
                        node_values[head_id] = node_values[tail_id] * partial_results[head_id][1]
                    elif head_label == '+':
                        node_values[head_id] = node_values[tail_id] + partial_results[head_id][1]
                    partial_results.pop( head_id )

                elif head_label.isidentifier(): # output node
                    node_values[head_id] = node_values[tail_id]

    print(node_values)
    return node_values


def generate_and_write_pe_memories( proj_dir, resource_graph, net_paths, dataflow_graph,placement_result, enter, exit_, C, T, pe_pipelining_stages, Nx, Ny, NUM_OPERANDS,IO_I,II, device ):

    global_node_enter_cycle = dict()
    node_and_edge_port = dict()
    edge_and_fanout_relative_travel_time = [0]* len( dataflow_graph.ordered_hyperedge_id_list() )


    for ix in range(len( dataflow_graph.ordered_hyperedge_id_list() )):
        edge_and_fanout_relative_travel_time[ix] = dict()

    ''' Start generate_unadjusted_global_timing'''

    leaf_nodes = dataflow_graph.get_leaf_nodes()

    # import pdb; pdb.set_trace()

    global_node_execute_cycle = dict()

    for leaf_node in leaf_nodes:

        leaf_edges = dataflow_graph.node_is_head_for( leaf_node )
        # if leaf_node == '8':
        # import pdb; pdb.set_trace()
        leaf_node_pe_xy = placement_result[leaf_node]

        for leaf_edge in leaf_edges:
            leaf_exit_noc_cycle =  cycle_for_pe_op( leaf_node_pe_xy, int(leaf_edge[1:])-1, exit_,C,T )

            global_node_execute_cycle[leaf_node] = leaf_exit_noc_cycle - pe_pipelining_stages
            global_node_execute_cycle, global_node_enter_cycle,node_and_edge_port,edge_and_fanout_relative_travel_time = generate_unadjusted_global_timing( leaf_node,leaf_edge, leaf_exit_noc_cycle,global_node_execute_cycle,global_node_enter_cycle,node_and_edge_port,edge_and_fanout_relative_travel_time, enter, exit_, C, T,placement_result,dataflow_graph,resource_graph,net_paths,pe_pipelining_stages, Nx,Ny,II, device )
            global_node_execute_cycle, global_node_enter_cycle,node_and_edge_port,edge_and_fanout_relative_travel_time = generate_unadjusted_global_timing( leaf_node,leaf_edge, leaf_exit_noc_cycle,global_node_execute_cycle,global_node_enter_cycle,node_and_edge_port,edge_and_fanout_relative_travel_time, enter, exit_, C, T,placement_result,dataflow_graph,resource_graph,net_paths,pe_pipelining_stages, Nx,Ny,II, device )

        print('global_node_execute_cycle')
        print(global_node_execute_cycle)
        global_node_execute_cycle, global_node_enter_cycle,latency = adjust_global_timing(global_node_execute_cycle,global_node_enter_cycle ) # TODO: have these be parameters
    print('global_node_execute_cycle')
    print(global_node_execute_cycle)
    critical_path_root_node = get_critical_path_root_node( global_node_execute_cycle )
    print(f"critical path root node {critical_path_root_node}")
    print("\n\nPRINTING CRITICAL PATH")

    current_node = critical_path_root_node
    while current_node not in leaf_nodes:
        print(f"executing node {current_node} ({dataflow_graph.get_node_attributes(current_node)['label']}) at {placement_result[current_node]} at cycle {int(global_node_execute_cycle[current_node])}")

        next_hyperedge = dataflow_graph.node_is_tail_for(current_node)

        # select next head: most critical node
        min_cycle_node = (0, 99999)
        print('next_hyperedge')
        print(next_hyperedge)

        # import pdb; pdb.set_trace()
        for critical_path_candidate in dataflow_graph.get_hyperedge_attribute( next_hyperedge, 'head'):
            try:
                if global_node_execute_cycle[critical_path_candidate] < min_cycle_node[1]:
                    min_cycle_node = (critical_path_candidate, global_node_execute_cycle[critical_path_candidate])
            except KeyError:
                import pdb; pdb.set_trace()
        current_node = min_cycle_node[0]
    print(f"executing node {current_node} ({dataflow_graph.get_node_attributes(current_node)['label']}) at {placement_result[current_node]} at cycle {int(global_node_execute_cycle[current_node])}")

    print("DONE PRINTING CRITICAL PATH\n\n")

    ''' Adjust all the timing according to most_negative_time'''

    # invert global_node_execute_cycle
    nodes_for_each_global_cycle = dict()
    for k, cycle in global_node_execute_cycle.items():

        if cycle in nodes_for_each_global_cycle:
            nodes_for_each_global_cycle[cycle].append( k )
        else:
            nodes_for_each_global_cycle[cycle] = [k]

    return latency

