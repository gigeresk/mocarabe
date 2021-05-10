import sys
sys.path.append("src")

import argparse
import re
import ast
import os
import json

import numpy as np

from rtl_gen import RTLGenerator

from dataflow_hypergraph import DataflowHypergraph

from resource_graph import ResourceGraph
from device import Device

def maxT( filename ):
    solfile = open(filename,'r')

    TMax = 0
    currentT = 0
    for line in solfile:
        match = re.compile('\d*(?=(] = 1$))').search(line)
        if match:
            currentT = int(match.group())
        if(currentT > TMax):
            TMax = currentT
    solfile.close()
    return TMax

def parseIndices(l):
    indexRegex = re.compile('(?<=\[)\d*(?=\])')
    enter = indexRegex.findall(l)
    indices = [ int(x) for x in enter ]
    return indices

''' asserts here are for:
python3 hwgen_develop.py -proj proj/int_ex2_--26-10-20-20.10.48/'''

parser = argparse.ArgumentParser(description='Script to help develop hwgen/RtlGen')
parser.add_argument('-proj',  type=str, required=True, help='proj directory')

sched_filename = ''
args = parser.parse_args()
sol_regex = re.compile('.*sol')
for root, dirs, files in os.walk(args.proj + '/schedule/'):
    for file in files:
        if sol_regex.match(file):
            sched_filename = args.proj + '/schedule/' + file

assert( sched_filename != '' )
print("sched_filename:",sched_filename)
assert( os.path.exists( sched_filename ) ), f"Schedule path {sched_filename} does not exist"

basename = os.path.basename( sched_filename )

Nx = int( re.compile('(?<=Nx)\d*').search(basename).group() )
Ny = int( re.compile('(?<=Ny)\d*').search(basename).group() )
C = int( re.compile('(?<=C)\d*').search(basename).group() )
P = int( re.compile('(?<=P)\d*').search(basename).group() )
T = int( re.compile('(?<=T)\d*').search(basename).group() )

h,v,enter,exit_, T = RTLGenerator.deserialize_schedule( sched_filename, Nx, Ny, C, P, T )

RTLGenerator.generate_and_write_noc_mux_memories( args.proj + f'rtl/', h, v, enter,exit_, Nx, Ny, C, P, T)

placement_filename = ''
args = parser.parse_args()
sol_regex = re.compile('.*json')
for root, dirs, files in os.walk(args.proj + '/placement/'):
    for file in files:
        if sol_regex.match(file):
            placement_filename = args.proj + '/placement/' + file

serialized_placement_file = open( placement_filename, "r" )
placement = serialized_placement_file.read()
placement_result = json.loads( placement )

dfg_path = ''
args = parser.parse_args()
sol_regex = re.compile('.*hgr')
for root, dirs, files in os.walk(args.proj + '/hls/'):
    for file in files:
        if sol_regex.match(file):
            dfg_path = args.proj + '/hls/' + file

''' CONSTANTS'''

IO_I = 2
IO_O = 1
layout = ''
pe_pipelining_stages = 2
noc_pipelining_stages = 2
unroll=1

NUM_OPERANDS = 2



''' YUCKY INITIALIZATIONS '''
dataflow_hgraph = DataflowHypergraph( dfg_path )
device = Device( Nx, Ny, C, T, IO_I,IO_O, layout, pe_pipelining_stages, noc_pipelining_stages, unroll, P, noc_pipelining_stages )

resource_graph = ResourceGraph( )
resource_graph.create( device )
net_paths = RTLGenerator.get_net_path_nodes( dataflow_hgraph, resource_graph, device, h, v, enter, exit_ )

op_addresses, op_port_select = RTLGenerator.generate_and_write_pe_memories( args.proj, resource_graph, net_paths, dataflow_hgraph,placement_result, enter, exit_, C, T, pe_pipelining_stages, Nx, Ny, NUM_OPERANDS,IO_I )


'''0,1, +'''
'''op addr memory'''

assert( hex(op_addresses[0][1][0][0])[2:] == "b" ),f"{op_addresses[0][1][0][0]} should be b (0xb)"
assert( hex(op_addresses[0][1][0][1])[2:] == "1" ),f"{op_addresses[0][1][0][1]} should be 1"
assert( hex(op_addresses[0][1][1][0])[2:] == "0" ),f"{op_addresses[0][1][1][0]} should be 0"
assert( hex(op_addresses[0][1][1][1])[2:] == "2" ),f"{op_addresses[0][1][1][1]} should be 2"

assert( hex(op_addresses[1][0][0][0])[2:] == "1" ),f"{op_addresses[1][0][0][0]} should be 1"
assert( hex(op_addresses[1][0][0][1])[2:] == "23" ),f"{op_addresses[1][0][0][1]} should be 23 (0x23)"
assert( hex(op_addresses[1][0][1][0])[2:] == "1a" ),f"{op_addresses[1][0][1][0]} should be 1a (0x1a)"
assert( hex(op_addresses[1][0][1][1])[2:] == "0" ),f"{op_addresses[1][0][1][1]} should be 0"

print('remember that pathfinder is currently unable to do the whole enter/exit at the same PE (no h/v) thing')

'''port select'''
assert( hex(op_port_select[0][1][0][0])[2:] == "0"),f"{op_port_select[0][1][0][0]} should be 0"
assert( hex(op_port_select[0][1][0][1])[2:] == "0"),f"{op_port_select[0][1][0][1]} should be 0"
assert( hex(op_port_select[0][1][1][0])[2:] == "0"),f"{op_port_select[0][1][1][0]} should be 0"
assert( hex(op_port_select[0][1][1][1])[2:] == "1"),f"{op_port_select[0][1][1][1]} should be 1"

assert( hex(op_port_select[1][0][0][0])[2:] == "1"),f"{op_port_select[1][0][0][0]} should be 1"
assert( hex(op_port_select[1][0][0][1])[2:] == "1"),f"{op_port_select[1][0][0][1]} should be 1"
assert( hex(op_port_select[1][0][1][0])[2:] == "0"),f"{op_port_select[1][0][1][0]} should be 0"
assert( hex(op_port_select[1][0][1][1])[2:] == "1"),f"{op_port_select[1][0][1][1]} should be 1"