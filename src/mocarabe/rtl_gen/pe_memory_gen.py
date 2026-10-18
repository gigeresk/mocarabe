import itertools
import copy
import json
import math

import numpy as np

from .header_gen import DATA_WIDTH
from .bitstream_gen import out_fields, pack

# A_val = execute - arrival - 5 is the SRL read address for an operand; the
# smallest value the original backward pass produced, kept as the lower bound
MIN_SRL_ADDRESS = 2


def get_net_path_nodes(
    dataflow_graph, resource_graph, device, h, v, enter, exit_
) -> list:
    net_paths = []
    # for every net
    for net_id, hyperedge_id in enumerate(
        dataflow_graph.ordered_hyperedge_id_iterator()
    ):
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
                                net_path.append(resource_graph.pe_out[(x, y, t)])
                                for io_o in range(device.IO_O):
                                    # will result in too many but thats ok
                                    net_path.append(
                                        resource_graph.pe_out_port[(x, y, io_o, t)]
                                    )
                                net_path.append(
                                    resource_graph.pe_out_switch[(x, y, c, t)]
                                )

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
                                net_path.append(resource_graph.pe_in[(x, y, t)])
                                for io_i in range(device.IO_I):
                                    # will result in too many but thats ok
                                    net_path.append(
                                        resource_graph.pe_in_port[(x, y, io_i, t)]
                                    )
                                net_path.append(
                                    resource_graph.pe_in_switch[(x, y, c, t)]
                                )
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


def routed_hops(head_pe_xy, net_id, h, v, enter, exit_, device):
    """Hops a net actually travels from its source to the switch where it exits
    at head_pe_xy.  Routes can detour around the torus when links are taken, so
    this can exceed the minimum torus distance.  Walks back from the exit with the
    same source priority (south, then west, then PE) as noc_mux_memory_gen.
    """
    T = device.schedule_length
    step = device.noc_pipelining_stages + 1
    x, y = head_pe_xy
    for c in range(device.physical_channels):
        for t in range(T):
            if exit_[x][y][c][net_id][t] == 1:
                break
        else:
            continue
        # the exit at t is fed by what was at this switch one hop earlier
        t = (t - step) % T
        hops = 0
        # each hop entered this switch noc_pipelining_stages + 1 cycles after the previous
        for _ in range(device.Nx * device.Ny * T + 1):
            prev_t = (t - step) % T
            if v[x][y][c][net_id][t] == 1:
                x, y, t = x, (y - 1) % device.Ny, prev_t
            elif h[x][y][c][net_id][t] == 1:
                x, y, t = (x - 1) % device.Nx, y, prev_t
            elif enter[x][y][c][net_id][t] == 1:
                return hops
            else:
                break
            hops += 1
        raise ValueError(f"net {net_id} has no route to its exit at {head_pe_xy}")
    raise ValueError(f"net {net_id} never exits at {head_pe_xy}")


def solve_global_timing(dataflow_graph, placement, h, v, enter, exit_, device):
    """Pick execute/enter cycles so every operand's SRL read address fits the FIFO.

    For a net u -> w the operand waits A_val = E_w - pipe - E_u - noc - 5 cycles
    in w's SRL (E = NoC enter cycle, noc = cycles on the NoC), which must be in
    [MIN_SRL_ADDRESS, device.fifo_depth - 1].  Each node's E is pinned modulo II to the
    slot the scheduler chose, so E = II*k + slot and the bounds become integer
    difference constraints on k, solved exactly with Bellman-Ford.
    """
    II = device.II
    pipe = device.pe_pipelining_stages
    C = device.physical_channels
    fifo_depth = device.fifo_depth
    nets = dataflow_graph.ordered_hyperedge_id_list()
    nodes = dataflow_graph.ordered_node_id_list()

    edge_and_fanout_node_cycles_on_noc = [dict() for _ in nets]
    node_and_edge_port = dict()
    slot = dict()
    edges = []  # (tail, head, noc cycles)

    for hyperedge_id in nets:
        net_id = int(hyperedge_id[1:]) - 1
        tail = dataflow_graph.get_hyperedge_attribute(hyperedge_id, "tail")[0]
        slot[tail] = cycle_for_pe_op(placement[tail], net_id, enter, C, II)
        for head in dataflow_graph.get_hyperedge_attribute(hyperedge_id, "head"):
            hops = routed_hops(placement[head], net_id, h, v, enter, exit_, device)
            noc = hops * (device.noc_pipelining_stages + 1)
            edge_and_fanout_node_cycles_on_noc[net_id][head] = noc
            edges.append((tail, head, noc))

    for node in nodes:
        for port, hyperedge_id in enumerate(dataflow_graph.get_predecessors(node)):
            node_and_edge_port[(node, hyperedge_id)] = port
        if node not in slot:
            # leaves never enter the NoC; they execute in the slot their operand exits
            hyperedge_id = dataflow_graph.node_is_head_for(node)[0]
            slot[node] = cycle_for_pe_op(
                placement[node], int(hyperedge_id[1:]) - 1, exit_, C, II
            )

    # k_j - k_i <= w  as an edge i -> j of weight w
    constraints = []
    for tail, head, noc in edges:
        base = pipe + noc + 5 + slot[tail] - slot[head]
        lo = math.ceil((base + MIN_SRL_ADDRESS) / II)
        hi = math.floor((base + fifo_depth - 1) / II)
        if lo > hi:
            raise ValueError(
                f"operand from node {tail} to node {head} cannot fit a {fifo_depth}-deep FIFO"
            )
        constraints.append((tail, head, hi))
        constraints.append((head, tail, -lo))

    k = {node: 0 for node in nodes}  # virtual source at distance 0 to every node
    for _ in range(len(nodes) + 1):
        changed = False
        for i, j, w in constraints:
            if k[i] + w < k[j]:
                k[j] = k[i] + w
                changed = True
        if not changed:
            break
    else:
        raise ValueError(
            f"no timing keeps every operand within the {fifo_depth}-deep PE FIFOs: "
            "operands that fan out to consumers far apart in time need deeper FIFOs"
        )

    global_node_enter_cycle = dict()
    global_node_execute_cycle = dict()
    tails = {tail for tail, _, _ in edges}
    for node in nodes:
        enter_cycle = II * k[node] + slot[node]
        if node in tails:
            global_node_enter_cycle[node] = enter_cycle
        global_node_execute_cycle[node] = enter_cycle - pipe

    return (
        global_node_execute_cycle,
        global_node_enter_cycle,
        node_and_edge_port,
        edge_and_fanout_node_cycles_on_noc,
    )


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


def assign_operand_ports(operands, num_ports):
    """Pick a PE input port (one SRL FIFO each) for every operand.

    Two operands of the same node need different ports, and different nets that
    reach a PE in the same slot need different ports (each port's mux captures
    one channel per slot).  One net feeding two nodes on a PE may use either.
    With two ports this is 2-colouring the conflict graph.
    """
    assert num_ports == 2, "operand port assignment assumes two PE input ports"
    conflicts = [set() for _ in operands]
    for i, a in enumerate(operands):
        for j in range(i + 1, len(operands)):
            b = operands[j]
            same_node = a["head"] == b["head"]
            same_slot = a["pe"] == b["pe"] and a["slot"] == b["slot"] and a["net"] != b["net"]
            if same_node or same_slot:
                conflicts[i].add(j)
                conflicts[j].add(i)

    ports = [None] * len(operands)
    for first in range(len(operands)):
        if ports[first] is not None:
            continue
        ports[first] = 0
        queue = [first]
        while queue:
            i = queue.pop()
            for j in conflicts[i]:
                if ports[j] is None:
                    ports[j] = 1 - ports[i]
                    queue.append(j)
                elif ports[j] == ports[i]:
                    a, b = operands[i], operands[j]
                    raise ValueError(
                        f"no PE port assignment at PE {a['pe']}: operands from nets "
                        f"{a['net']} (node {a['head']}, slot {a['slot']}) and {b['net']} "
                        f"(node {b['head']}, slot {b['slot']}) conflict"
                    )
    return ports


def generate_op_addresses_and_op_port_select(
    device,
    NUM_OPERANDS,
    T,
    exit_,
    dataflow_graph,
    global_node_execute_cycle,
    global_node_enter_cycle,
    placement,
    node_and_edge_port,
    edge_and_fanout_node_cycles_on_noc,
):

    Nx = device.Nx
    Ny = device.Ny
    C = device.physical_channels
    op_addresses = np.zeros((Nx, Ny, NUM_OPERANDS, T), dtype=int)
    op_port_select = np.zeros((Nx, Ny, NUM_OPERANDS, T), dtype=int)

    operands = []  # one per (net, head) pair; a net listing a head twice (x*x) gives two
    for hyperedge_id in dataflow_graph.ordered_hyperedge_id_iterator():
        net_id = int(hyperedge_id[1:]) - 1
        tail_node = dataflow_graph.get_hyperedge_attributes(hyperedge_id)["tail"][0]
        for head_node in dataflow_graph.get_hyperedge_attribute(hyperedge_id, "head"):
            head_pe_xy = placement[head_node]
            channel, t = get_exit_channel_and_cycle(
                exit_, head_pe_xy[0], head_pe_xy[1], net_id, C, T
            )
            operands.append(
                {
                    "net": hyperedge_id,
                    "tail": tail_node,
                    "head": head_node,
                    "pe": tuple(head_pe_xy),
                    "slot": t % T,
                    "channel": channel,
                    "arrival": global_node_enter_cycle[tail_node]
                    + edge_and_fanout_node_cycles_on_noc[net_id][head_node],
                }
            )

    ports = assign_operand_ports(operands, device.IO_I)

    pe_in_events = []  # (arrival_time, port, head_pe_xy, tail_node)
    address_owner = dict()
    for operand, port in zip(operands, ports):
        operand["port"] = port
        x, y = operand["pe"]
        execute_time_for_this_op = global_node_execute_cycle[operand["head"]]
        load_time = (execute_time_for_this_op - 2) % T

        op_port_select[x][y][port][operand["slot"]] = operand["channel"]

        A_val = execute_time_for_this_op - operand["arrival"] - 5
        assert 0 <= A_val < device.fifo_depth, (
            f"SRL address {A_val} for node {operand['head']} is outside the FIFO"
        )
        owner = address_owner.setdefault((x, y, port, load_time), operand["head"])
        assert owner == operand["head"], (
            f"nodes {owner} and {operand['head']} both load from PE {(x, y)} "
            f"port {port} in slot {load_time}"
        )
        op_addresses[x][y][port][load_time] = A_val

        pe_in_events.append((operand["arrival"], port, list(operand["pe"]), operand["tail"]))

    return op_addresses, op_port_select, pe_in_events, operands


def is_io_label(label):
    """inputs, outputs and constants: named or numeric DFG nodes (IO PEs)"""
    return label.isidentifier() or label.lstrip("-").isnumeric()


def input_name(dataflow_graph, node):
    """The host-side input a root node reads; split_input_fanout copies share it"""
    attributes = dataflow_graph.get_node_attributes(node)
    return attributes.get("copy_of", attributes["label"])


def shared_input_value(name, names, iteration, data_width):
    """Test value of input `name` in one iteration on the shared input bus: a
    constant is its own value; other inputs differ by name and by iteration."""
    if name.lstrip("-").isnumeric():
        value = int(name)
    else:
        value = 29 * names.index(name) + 11 * iteration + 3
    return value % 2**data_width


""" Given values for all input nodes and a DFG, return a dict with every node's value"""


def get_node_values(input_values, dataflow_graph, data_width=DATA_WIDTH):
    # note that we assume 2-input operations

    known_node_values = copy.deepcopy(input_values)

    unknown_nodes = dataflow_graph.ordered_node_id_list()
    for node, value in known_node_values.items():
        unknown_nodes.remove(node)

    while len(unknown_nodes) > 0:
        num_unknown = len(unknown_nodes)
        for unknown_node in unknown_nodes:
            parent_nodes = dataflow_graph.get_parent_nodes(unknown_node)

            both_parents_are_known = all(
                [x in known_node_values.keys() for x in parent_nodes]
            )

            if both_parents_are_known and len(parent_nodes) > 0:
                head_label = dataflow_graph.get_node_attribute(unknown_node, "label")

                # the PE datapath is data_width bits wide and wraps
                if head_label == "*":
                    known_node_values[unknown_node] = (
                        known_node_values[parent_nodes[0]]
                        * known_node_values[parent_nodes[1]]
                    ) % 2**data_width
                elif head_label == "+":
                    known_node_values[unknown_node] = (
                        known_node_values[parent_nodes[0]]
                        + known_node_values[parent_nodes[1]]
                    ) % 2**data_width
                elif is_io_label(head_label) and parent_nodes[0] == parent_nodes[1]:
                    # an output node (one input) shows its operand
                    known_node_values[unknown_node] = known_node_values[parent_nodes[0]]
                else:
                    assert True, (
                        f"Unsupported operand {head_label}.  Please add support"
                    )

                unknown_nodes.remove(unknown_node)

        if len(unknown_nodes) == num_unknown:
            stuck = {
                n: dataflow_graph.get_node_attribute(n, "label") for n in unknown_nodes
            }
            raise ValueError(f"cannot compute values for DFG nodes {stuck}")

    return known_node_values


def generate_and_write_pe_memories(
    proj_dir,
    resource_graph,
    net_paths,
    dataflow_graph,
    placement_result,
    enter,
    exit_,
    NUM_OPERANDS,
    IO_I,
    II,
    device,
    h=None,
    v=None,
):
    # h, v: the schedule's routed links; operand latency follows the actual route

    (
        global_node_execute_cycle,
        global_node_enter_cycle,
        node_and_edge_port,
        edge_and_fanout_node_cycles_on_noc,
    ) = solve_global_timing(dataflow_graph, placement_result, h, v, enter, exit_, device)

    """ Adjust all the timing according to most_negative_time"""
    global_node_execute_cycle, global_node_enter_cycle, latency, startup_latency = (
        adjust_global_timing(global_node_execute_cycle, global_node_enter_cycle, device)
    )

    """ What we're really after """
    # edge_each_fanout_write_into_srl_time does not really have to be returned
    op_addresses, op_port_select, pe_in_events, operands = (
        generate_op_addresses_and_op_port_select(
            device,
            NUM_OPERANDS,
            device.T,
            exit_,
            dataflow_graph,
            global_node_execute_cycle,
            global_node_enter_cycle,
            placement_result,
            node_and_edge_port,
            edge_and_fanout_node_cycles_on_noc,
        )
    )

    for operand in range(NUM_OPERANDS):
        for x in range(device.Nx):
            for y in range(device.Ny):
                string = ""
                for t in range(device.T):
                    string += hex(op_addresses[x][y][operand][t])[2:] + "\n"
                this_file = open(
                    proj_dir + f"/rtl/op{operand + 1}_addr_memory_x{x}_y{y}.dat", "w+"
                )
                this_file.write(string)
                this_file.close()

    for operand in range(NUM_OPERANDS):
        for x in range(device.Nx):
            for y in range(device.Ny):
                string = ""
                for t in range(device.T):
                    string += bin(op_port_select[x][y][operand][t])[2:] + "\n"
                this_file = open(
                    proj_dir + f"/rtl/pe_mux_x{x}_y{y}_sel_mem{operand}.dat", "w+"
                )
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

    II = device.II
    data_width = device.data_width
    roots = sorted(dataflow_graph.get_all_root_nodes(), key=int)
    labels = {n: dataflow_graph.get_node_attribute(n, "label") for n in dataflow_graph.ordered_node_id_list()}

    # assert_values
    if device.shared_io:
        # one input bus: each input is sampled from it at its own execute cycle
        names = sorted({input_name(dataflow_graph, n) for n in roots})
        input_slots = {}
        for node in roots:
            slot = global_node_execute_cycle[node] % II
            if slot in input_slots:
                raise ValueError(
                    f"inputs {input_slots[slot]} and {node} both read the shared input in slot {slot}"
                )
            input_slots[slot] = node

        def iteration_inputs(iteration):
            return {
                n: shared_input_value(input_name(dataflow_graph, n), names, iteration, data_width)
                for n in roots
            }

        root_node_values = iteration_inputs(0)
        root_node_values_2nd = iteration_inputs(1)
    else:
        root_node_values = {}
        for input_node in roots:
            x, y = placement_result[input_node]
            root_node_values[input_node] = global_node_execute_cycle[input_node] + 100 * (
                x + y * device.Nx
            )  # to prevent 0
        # Second-iteration expected values: each root input shifts by II each period
        root_node_values_2nd = {node: val + II for node, val in root_node_values.items()}
        # the IO PEs see the testbench's formula through a data_width-bit port
        for values in (root_node_values, root_node_values_2nd):
            for node in values:
                values[node] %= 2**data_width

    assert_values = get_node_values(root_node_values, dataflow_graph, data_width)
    assert_values_2nd = get_node_values(root_node_values_2nd, dataflow_graph, data_width)

    # Output port: an output (IO leaf) reaches its IO PE's operand port in the slot
    # its net exits; io_out registers that port then and shows it one cycle later.
    # Each slot drives io_out from at most one output.
    leaves = set(dataflow_graph.get_leaf_nodes())
    o_fields, out_w = out_fields(device.Nx * device.Ny)
    out_rows = [0] * II
    slot_output = dict()
    io_outputs = []
    for operand in operands:
        node = operand["head"]
        if node not in leaves or not is_io_label(labels[node]):
            continue
        tap = operand["arrival"] + 3  # when pe_in{port} shows it
        slot = tap % II
        assert slot == operand["slot"], (
            f"output {node} reaches its PE at cycle {tap}, not in exit slot {operand['slot']}"
        )
        if slot in slot_output:
            if device.shared_io:
                raise ValueError(
                    f"outputs {slot_output[slot]} and {node} both use io_out in slot {slot}"
                )
            continue  # without shared IO, extra outputs stay off io_out
        slot_output[slot] = node
        x, y = operand["pe"]
        row = {"valid": 1, "port": operand["port"], "pe": x + y * device.Nx}
        out_rows[slot] = pack(row, o_fields, f"output {node}")
        io_outputs.append({"node": node, "label": labels[node], "cycle": tap + 1})

    with open(proj_dir + "/rtl/io_out_memory.dat", "w") as f:
        f.write("".join(format(row, f"0{out_w}b") + "\n" for row in out_rows))

    Nx = resource_graph.Nx

    # Collect all assertion events as (cycle, signal_expr, expected, label)
    events = []

    # First iteration: pe_out at node's NoC-enter cycle
    for cycle, nodes in enter_noc_cycle2node.items():
        for node in nodes:
            x, y = placement_result[node]
            events.append(
                (
                    cycle,
                    f"pe_out[{x} + {Nx}*{y}]",
                    assert_values[node],
                    f"node {node} iter1",
                )
            )

    # Second iteration: same PEs II cycles later, with next period's data
    for cycle, nodes in enter_noc_cycle2node.items():
        for node in nodes:
            x, y = placement_result[node]
            events.append(
                (
                    cycle + II,
                    f"pe_out[{x} + {Nx}*{y}]",
                    assert_values_2nd[node],
                    f"node {node} iter2",
                )
            )

    # Operand arrival: pe_in{port} at each head PE when the value is visible at the mux output.
    # arrival_time is when the data reaches the last NoC switch; +2 for the o_to_pe pipeline
    # (o_to_pe_r + o_to_pe_pipe), so the mux output is stable at sim time arrival_time+3
    # (mux_to_pe-after-g(arrival+2), which is what op_reg will capture).
    for arrival_time, port, head_pe_xy, tail_node in pe_in_events:
        hx, hy = head_pe_xy
        events.append(
            (
                arrival_time + 3,
                f"pe_in{port}[{hx} + {Nx}*{hy}]",
                assert_values[tail_node],
                f"operand to PE({hx},{hy}) port {port} from node {tail_node}",
            )
        )

    # Output port: io_out and its valid strobe, both iterations
    for output in io_outputs:
        node = output["node"]
        for cycle, values, it in ((output["cycle"], assert_values, 1), (output["cycle"] + II, assert_values_2nd, 2)):
            events.append((cycle, "io_out", values[node], f"output {output['label']} iter{it}"))
            events.append((cycle, "io_out_valid", 1, f"output {output['label']} iter{it} valid"))

    events.sort(key=lambda e: e[0])
    assert_count = len(events)

    if device.shared_io:
        # the input bus, cycle by cycle from run cycle 0, for every iteration that
        # reaches an assertion: input n's iteration k is sampled at E_n + k*II
        length = max(e[0] for e in events) + II + 1
        stream = [0] * length
        for node in roots:
            execute = global_node_execute_cycle[node]
            for cycle in range(execute % II, length, II):
                stream[cycle] = shared_input_value(
                    input_name(dataflow_graph, node), names, (cycle - execute) // II, data_width
                )
        digits = -(-data_width // 4)
        with open(proj_dir + "/rtl/io_stream.hex", "w") as f:
            f.write("".join(f"{value:0{digits}x}\n" for value in stream))

        # what a host (or the TinyTapeout test) needs to drive the chip
        schedule = {
            "data_width": data_width,
            "ii": II,
            "fifo_depth": device.fifo_depth,
            "inputs": [
                {"node": n, "name": input_name(dataflow_graph, n), "cycle": global_node_execute_cycle[n]}
                for n in roots
            ],
            "outputs": io_outputs,
            "nodes": {
                n: {"label": labels[n], "operands": dataflow_graph.get_parent_nodes(n)}
                for n in dataflow_graph.ordered_node_id_list()
            },
            "cycles": "input n is sampled at run cycle cycle + k*II for iteration k; "
            "output n is on io_out at run cycle cycle + k*II",
        }
        with open(proj_dir + "/rtl/io_schedule.json", "w") as f:
            json.dump(schedule, f, indent=2)

    asserts_string = ""
    last_cycle = 0
    for cycle, grp in itertools.groupby(events, key=lambda e: e[0]):
        step = cycle - last_cycle
        asserts_string += f"        #{step} //cycle {cycle}\n"
        for _, signal, expected, label in grp:
            asserts_string += f'        assert({signal} == {expected}) $display("OK: {signal}=={expected} ({label})");\n'
            asserts_string += f'        else begin fail_count = fail_count + 1; $display("Assert error: {signal}==%0d @{cycle}, should be {expected} ({label})", {signal}); end\n'
        last_cycle = cycle

    asserts_string += "        if (fail_count == 0)\n"
    asserts_string += f'            $display("\\n=== PASS: all {assert_count} assertions passed ===");\n'
    asserts_string += "        else\n"
    asserts_string += f'            $display("\\n=== FAIL: %0d of {assert_count} assertions failed ===", fail_count);\n'
    asserts_string += "        #10\n"
    asserts_string += "        $finish;\n"

    return op_addresses, op_port_select, asserts_string, latency
