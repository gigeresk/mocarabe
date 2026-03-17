#!/usr/bin/env python3
"""
Regenerate RTL memories and testbench for an existing project using
the fixed generator code.
"""

import sys
import json
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mocarabe.cad.netlist import Netlist
from mocarabe.device import Device
from mocarabe.rtl_gen import RTLGenerator
from mocarabe.resource_graph import ResourceGraph

PROJ_DIR = "proj/int_adder_chain_--14-03-26-20.56.47/"
HGR_FILE = PROJ_DIR + "hgr/int_adder_chain.hgr"
SOL_FILE = PROJ_DIR + "schedule/-Nx2-Ny4-C20-P7-T3.sol"
PLACEMENT_FILE = PROJ_DIR + "placement/dfg_node_to_pe_xy.json"
RTL_DIR = PROJ_DIR + "rtl/"

Nx = 2
Ny = 4
C = 20
T = 3
P = 7  # num nets
II = 3
noc_pipelining_stages = 2
pe_pipelining_stages = 5
NUM_OPERANDS = 2
IO_I = 2
IO_O = 1

print("Loading schedule...")
h, v, enter, exit_, T = RTLGenerator.deserialize_schedule(SOL_FILE, Nx, Ny, C, P, T)
print(f"T={T}")

print("Regenerating NoC mux memories...")
RTLGenerator.generate_and_write_noc_mux_memories(
    RTL_DIR, h, v, enter, exit_, Nx, Ny, C, P, T, noc_pipelining_stages
)

print("Loading dataflow graph and placement...")
dataflow_graph = Netlist(dfg_path=HGR_FILE, unroll_factor=1)

with open(PLACEMENT_FILE) as f:
    placement_raw = json.load(f)
# Try both string and int keys to match what Netlist uses
placement = {k: tuple(v) for k, v in placement_raw.items()}
placement.update({int(k): tuple(v) for k, v in placement_raw.items()})

layout = ""
device = Device(
    Nx,
    Ny,
    C,
    T,
    T,
    IO_I,
    IO_O,
    layout,
    pe_pipelining_stages,
    noc_pipelining_stages,
    1,
    P,
    II,
)

resource_graph = ResourceGraph()
resource_graph.create(device)

net_paths = RTLGenerator.get_net_path_nodes(
    dataflow_graph, resource_graph, device, h, v, enter, exit_
)

print("Regenerating PE memories...")
op_addresses, op_port_select, asserts_string, latency = (
    RTLGenerator.generate_and_write_pe_memories(
        PROJ_DIR,
        resource_graph,
        net_paths,
        dataflow_graph,
        placement,
        enter,
        exit_,
        NUM_OPERANDS,
        IO_I,
        II,
        device,
    )
)

print("Regenerating testbench...")
RTLGenerator.testbench_gen(RTL_DIR, Nx, Ny, C, asserts_string)

print("Done.")
print("Assertions:")
print(asserts_string)
