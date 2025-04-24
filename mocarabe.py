import argparse
import os
from datetime import datetime
import shutil
import collections
import warnings

import numpy as np
from networkx.drawing.nx_pydot import write_dot

from src.dataflow_hypergraph import DataflowHypergraph
from src.device import Device
import src.pe_allocator as pe_alloc
import src.placer as placr
import src.scheduler as schedulr
from src.rtl_gen import RTLGenerator
from src.file_util import FilePathsHelper
from src.resource_graph import ResourceGraph

parser = argparse.ArgumentParser(description='Space-Time ILP Scheduler')
parser.add_argument('-dfg', metavar='dfg dir', required=True, type=str, help='path to dfg dir, contains .hgr file')
parser.add_argument('-II', metavar='initiation interval', required=True, type=int, default=1, help="how often we can input new data into the system")
parser.add_argument('-C', metavar='channel width', type=int, default=1, help="physical channel width for NoC")
parser.add_argument('--log', metavar='log', type=str, default='log.csv', help="log, useful for running experiments")
parser.add_argument('--tag', metavar='tag for logging', type=str, default="-", help="tag for logging")
parser.add_argument('--place_time', metavar='placement duration (minutes)', type=float, default=0.01, help="max duration for cgra placement")
# parser.add_argument('-T', metavar='schedule length', type=int, default = 0, help='schedule length (optional upper bound)')
parser.add_argument('--unroll', help='DFG unroll factor, default is 1, 0 for automatic unroll (max is II)', type=int, default = 1)
parser.add_argument('--sched_method', metavar='scheduling_method', type=str, default='PF', help="sched method, either ILP or PF")
parser.add_argument('-iod', metavar='io diffusion', type=float, default=1.0)
parser.add_argument('-ard', metavar='arith diffusion', type=float, default=1.0)

parser.add_argument('--noc_pipe', metavar='noc pipelining', type=float, default=2 )
parser.add_argument('--pe_pipe', metavar='pe pipelining', type=int, default=5 )

args = parser.parse_args()

dfg_dir = args.dfg
II = args.II
C = args.C
log_file = args.log
tag = args.tag
placement_time_delta = args.place_time
schedule_length = args.II
unroll_factor = args.unroll
sched_method = args.sched_method
io_diffusion = args.iod
arith_diffusion = args.ard

noc_pipelining_stages = args.noc_pipe
pe_pipelining_stages = args.pe_pipe
# num of PE outputs
IO_O = 1
IO_I = 2
NUM_OPERANDS = 2

print( '\n\nCGRA-ILP: High-Level Synthesis Compiler for Mocarabe\n\n' )
# user warnings
class bcolors:
    WARNING = '\033[93m'
    ENDC = '\033[0m'

if schedule_length != II:
    warnings.warn(f"{bcolors.WARNING}T != II: this is experimental{bcolors.ENDC}")
if io_diffusion > II:
    warnings.warn(f"{bcolors.WARNING}iod > II: trying to pack more input nodes in a PE than the modulo schedule can handle{bcolors.ENDC}")
if arith_diffusion > II:
    warnings.warn(f"{bcolors.WARNING}ard > II: trying to pack more operations in a PE than the modulo schedule can handle{bcolors.ENDC}")

assert( os.path.exists( dfg_dir ) ), f"{os.path.realpath(dfg_dir)} does not exist.  Have you run gcc?"
assert( sched_method == 'ILP' or sched_method == 'PF' ),  "sched_method must be either 'ILP' or 'PF' "
assert( IO_O > 0 and IO_O <= C), "0 < IO_O <= C must hold"

''' Environment Setup '''
dfg_dir = dfg_dir.strip("/")
benchmark_name = os.path.basename( dfg_dir )
timestamp_suffix = datetime.now().strftime("--%d-%m-%y-%H.%M.%S")
file_helper = FilePathsHelper( 'proj/', benchmark_name, timestamp_suffix )
file_helper.mk_proj_subdirectories()
file_helper.log_file = log_file

print( "Copying DFG files from hls/ to {}hls/".format( file_helper.proj_dir ) )
shutil.copy( os.path.join( dfg_dir, benchmark_name+'.hgr'), file_helper.hgr_dir + benchmark_name + '.hgr' )

print( "Copying verilog files from rtl/rtl-for-sim/ to {}rtl/".format( file_helper.proj_dir ) )
for rtl_file in ['pe_mux_2_input.sv','pe_srl.v','pe_2_input.sv','pe_mux_3_input.sv','SRL16E.v','SRLC32E.v', 'SRL64.v','torus_switch.sv', 'mocarabe.sv','mocarabe.h']:
    shutil.copy( os.path.join( 'rtl','rtl', rtl_file ), os.path.join( file_helper.proj_dir, 'rtl', rtl_file ) )

if not os.path.exists('svg'):
    print( "Creating 'svg' directory")
    os.makedirs('svg')

# Deserialize and unroll dataflow hypergraph
if unroll_factor == 0:

    # If there are fewer than II instances of a given operator, unroll by II
    # This is to keep PE utilization high for small benchmarks
    dataflow_hgraph = DataflowHypergraph( os.path.join( dfg_dir, benchmark_name+".hgr"), unroll_factor=1 )
    arith_oprtrs = collections.Counter( dataflow_hgraph.extract_node_arithmetic_operators().values() )
    io_operators = collections.Counter( dataflow_hgraph.extract_node_io_operators().values() )
    if '+' not in arith_oprtrs: arith_oprtrs['+'] = 0
    if '*' not in arith_oprtrs: arith_oprtrs['*'] = 0

    if (arith_oprtrs['+']  < II and arith_oprtrs['+']  != 0) or (arith_oprtrs['*'] < II and arith_oprtrs['*'] != 0) or (io_operators['IO'] < II and io_operators['IO'] != 0):
        unroll_factor = II
    else:
        unroll_factor = 1

    dataflow_hgraph = DataflowHypergraph( os.path.join(dfg_dir,benchmark_name+".hgr"), unroll_factor )
    print(f'Auto-Unroll factor: {unroll_factor}')
else:
    dataflow_hgraph = DataflowHypergraph( dfg_path= os.path.join(dfg_dir,benchmark_name+".hgr"), unroll_factor=unroll_factor )

write_dot( dataflow_hgraph.to_graph(), os.path.join(file_helper.dot_dir, benchmark_name + ".dot") )


''' PE Allocation '''

Nx, Ny, device_map =  pe_alloc.ClosestFactorsAllocator().allocate_pes( dataflow_hgraph, II, io_diffusion, arith_diffusion )
print(f'Nx={Nx}, Ny={Ny}')
print( pe_alloc.to_string( device_map ) )
num_partitions_given_to_operator = collections.Counter( np.ndarray.flatten( device_map ) )

''' Partitioning/Packing and Placement '''
placement_start_time = datetime.now()
partition_filename = file_helper.partition_dir + benchmark_name + "-K" + str(Nx*Ny) + "-U" + str( unroll_factor )

dfg_node_to_pe_xy_map_, pe_operators = placr.IlpAndSimulatedAnnealingPlacer().place( dataflow_hgraph, Nx*Ny, num_partitions_given_to_operator, partition_filename + '.sol', II,placement_time_delta,Nx,Ny,file_helper.log_dir )

# serialize placement
file_helper.write_list_to_file( file_helper.placement_dir + 'dfg_node_to_pe_xy.json', dfg_node_to_pe_xy_map_ )

# serialize placed netlist (scheduler input)
serialized_placed_netlist = placr.serialize_placed_netlist( dataflow_hgraph, dfg_node_to_pe_xy_map_, True )
placed_netlist = placr.create_placed_netlist( dataflow_hgraph, dfg_node_to_pe_xy_map_, True )

netfile = open(file_helper.netlist_filepath, "w+")
netfile.write(serialized_placed_netlist)
netfile.close()

placement_time_delta = datetime.now() - placement_start_time

''' Scheduling '''
num_nets = len( dataflow_hgraph.get_hyperedge_id_set() )
file_helper.schedule_filepath = file_helper.schedule_dir + benchmark_name +'-Nx%d-Ny%d-C%d-num_nets%d-T%d' % ( Nx, Ny, C, num_nets, schedule_length ) + '.sol'

layout = ''
device = Device( Nx, Ny, C, schedule_length, IO_I, IO_O, layout, pe_pipelining_stages, noc_pipelining_stages, unroll_factor, num_nets, II )
if sched_method == 'ILP':
    boundingBoxEnabled = False

    scheduled_netlist = schedulr.IlpScheduler().run_scheduling_with_timeout( device, placed_netlist, placement_time_delta,file_helper,num_partitions_given_to_operator, tag )

    if scheduled_netlist != None:
        ''' RTL '''
        T = II

        print( '--------------Generating Simulation RTL--------------\n' )

        h,v,enter,exit_, T = RTLGenerator.deserialize_schedule( file_helper.schedule_filepath, Nx, Ny, device.physical_channels, num_nets, T )

        RTLGenerator.generate_and_write_noc_mux_memories( file_helper.rtl_dir, h, v, enter,exit_, Nx, Ny, C, num_nets, T, noc_pipelining_stages)

        ''' verify scheduled netlist channel utilization '''
        utilization_factor = scheduled_netlist.physical_channel_utilization_factor( device.Nx, device.Ny, device.physical_channels, T )
        unused_xy = scheduled_netlist.unused_xy( device.Nx, device.Ny, device.physical_channels, T )

        verilog_header = RTLGenerator.verilog_header_gen( file_helper.proj_dir + 'rtl/', device, pe_operators )

        verilog_header_filename = file_helper.rtl_dir + 'benchmark.h'
        file_helper.write_string_to_file( verilog_header_filename, verilog_header )

        resource_graph = ResourceGraph( )
        resource_graph.create( device )

        net_paths = RTLGenerator.get_net_path_nodes( dataflow_hgraph, resource_graph, device, h, v, enter, exit_ )
        op_addresses, op_port_select, asserts_string, latency6 = RTLGenerator.generate_and_write_pe_memories( file_helper.proj_dir, resource_graph, net_paths, dataflow_hgraph,dfg_node_to_pe_xy_map_, enter, exit_, NUM_OPERANDS,IO_I ,II, device)

        RTLGenerator.testbench_gen( file_helper.proj_dir + 'rtl/',  Nx, Ny, C, asserts_string )

        print("To start a simultation with xsim (Vivado simulator):\n")
        print( f"cd {file_helper.proj_dir}/rtl/" )
        print( "xvlog --sv mocarabe.sv pe_2_input.sv torus_switch.sv pe_srl.v pe_mux_2_input.sv pe_mux_3_input.sv SRL16E.v SRLC32E.v SRL64.v mocarabe_tb.sv" )
        print( "xelab -debug typical mocarabe_tb -s mocarabe_sim" )
        print( "xsim mocarabe_sim" )
        print( "----" )

        print("For a visualization of the schedule:")
        print( "python3 src/torus_gui_freeze.py --proj {} --zoom 5".format( file_helper.proj_dir) )
        print("\n")

elif sched_method == 'PF':
    warnings.warn(f"{bcolors.WARNING} PathFinder scheduler not maintained to the same level as ILP scheduler")
    file_helper.tag = tag
    device.num_partitions_given_to_operator = num_partitions_given_to_operator
    scheduled_netlist = schedulr.PathfinderScheduler().run_scheduling_with_timeout( device, placed_netlist, placement_time_delta,file_helper,num_partitions_given_to_operator, tag )

    print( "python3 src/torus_gui_freeze.py --proj {} --zoom 5".format( file_helper.proj_dir) )
    verilog_header = RTLGenerator.verilog_header_gen( file_helper.proj_dir + 'rtl/', device, pe_operators )
    verilog_header_filename = file_helper.rtl_dir + 'benchmark.h'
    file_helper.write_string_to_file( verilog_header_filename, verilog_header )