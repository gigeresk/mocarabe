import argparse
import os
import random
from datetime import datetime
import shutil
import collections
import warnings

import numpy as np
from networkx.drawing.nx_pydot import write_dot

from mocarabe.cad.netlist import Netlist
from mocarabe.device import Device, load_device_spec, check_dfg_fits
import mocarabe.pe_allocator as pe_alloc
import mocarabe.cad.placer as placr
import mocarabe.cad.scheduler as schedulr
from mocarabe.rtl_gen import RTLGenerator
from mocarabe.rtl_gen.header_gen import DATA_WIDTH, FIFO_DEPTH, FIFO_DEPTHS
from mocarabe.file_util import FilePathsHelper
from mocarabe.resource_graph import ResourceGraph

from mocarabe.sim import Sim


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Space-Time ILP Scheduler")
    parser.add_argument(
        "-dfg",
        metavar="dfg dir",
        required=True,
        type=str,
        help="path to dfg dir, contains .hgr file",
    )
    parser.add_argument(
        "-II",
        metavar="initiation interval",
        required=True,
        type=int,
        default=1,
        help="how often we can input new data into the system",
    )
    parser.add_argument(
        "-C",
        metavar="channel width",
        type=int,
        default=None,
        help="physical channel width for NoC (default 1, or the --device file's channels)",
    )
    parser.add_argument(
        "--max_C",
        metavar="max channel width",
        type=int,
        default=None,
        help="if scheduling fails, keep raising C up to this value",
    )
    parser.add_argument(
        "--device",
        metavar="device file",
        type=str,
        default=None,
        help="fixed device JSON (see devices/); default sizes the array to the DFG",
    )
    parser.add_argument(
        "--bitstream",
        choices=["hard", "soft"],
        default="hard",
        help="default configuration in benchmark.h: hard ($readmem) or soft (programmed "
        "serially through cfg_en/cfg_data); every project gets both",
    )
    parser.add_argument(
        "--cfg_width",
        metavar="soft bitstream word width",
        type=int,
        default=1,
        help="bits per clock on cfg_data when programming the soft bitstream",
    )
    parser.add_argument(
        "--ii_max",
        metavar="max initiation interval",
        type=int,
        default=None,
        help="schedule slots the soft bitstream's memories hold (default: the --device "
        "file's ii_max, else II)",
    )
    parser.add_argument(
        "--data_width",
        metavar="datapath bits",
        type=int,
        default=DATA_WIDTH,
        help=f"PE datapath width in bits (default {DATA_WIDTH})",
    )
    parser.add_argument(
        "--fifo_depth",
        type=int,
        choices=FIFO_DEPTHS,
        default=FIFO_DEPTH,
        help=f"depth of each PE operand FIFO; an operand waits at most depth-1 cycles "
        f"(default {FIFO_DEPTH})",
    )
    parser.add_argument(
        "--shared_io",
        action="store_true",
        help="all IO PEs share one input bus and the outputs share io_out (a chip's pins): "
        "every input and every output gets its own schedule slot, so II must be at least "
        "the number of inputs and of outputs",
    )
    parser.add_argument(
        "--log",
        metavar="log",
        type=str,
        default="log.csv",
        help="log, useful for running experiments",
    )
    parser.add_argument(
        "--tag",
        metavar="tag for logging",
        type=str,
        default="-",
        help="tag for logging",
    )
    parser.add_argument(
        "--place_time",
        metavar="placement duration (minutes)",
        type=float,
        default=0.01,
        help="max duration for cgra placement",
    )
    parser.add_argument(
        "--sched_time",
        metavar="scheduling duration (seconds)",
        type=float,
        default=30,
        help="max duration for ILP scheduling (SCIP time limit in seconds)",
    )
    # parser.add_argument('-T', metavar='schedule length', type=int, default = 0, help='schedule length (optional upper bound)')
    parser.add_argument(
        "--unroll",
        help="DFG unroll factor, default is 1, 0 for automatic unroll (max is II)",
        type=int,
        default=1,
    )
    parser.add_argument(
        "--split_input_fanout",
        action="store_true",
        help="give each consumer of an input its own IO node (avoids deep FIFO waits)",
    )
    parser.add_argument(
        "--sched_method",
        metavar="scheduling_method",
        type=str,
        default="PF",
        help="sched method, either ILP or PF",
    )
    parser.add_argument("-iod", metavar="io diffusion", type=float, default=1.0)
    parser.add_argument("-ard", metavar="arith diffusion", type=float, default=1.0)

    parser.add_argument("--noc_pipe", metavar="noc pipelining", type=float, default=2)
    parser.add_argument("--pe_pipe", metavar="pe pipelining", type=int, default=5)
    parser.add_argument(
        "--seed",
        metavar="random seed",
        type=int,
        default=0,
        help="seed for SA placer and SCIP solvers (default 0 = deterministic)",
    )
    return parser.parse_args(argv)


def shared_io_groups(dataflow_hgraph, placement, II):
    """With shared IO, inputs read one bus and outputs drive one port, so the
    scheduler must give the inputs' NoC enters (and the outputs' NoC exits)
    different slots.  Returns [("enter", [(x, y, net)]), ("exit", [(x, y, net)])]."""
    inputs, outputs = [], []
    leaves = set(dataflow_hgraph.get_leaf_nodes())
    for net, hyperedge_id in enumerate(dataflow_hgraph.ordered_hyperedge_id_iterator()):
        tail = dataflow_hgraph.get_hyperedge_attribute(hyperedge_id, "tail")[0]
        if not dataflow_hgraph.node_is_head_for(tail):
            inputs.append((*placement[tail], net))
        for head in dict.fromkeys(dataflow_hgraph.get_hyperedge_attribute(hyperedge_id, "head")):
            if head in leaves:
                outputs.append((*placement[head], net))
    for kind, members in (("inputs", inputs), ("outputs", outputs)):
        if len(members) > II:
            raise ValueError(
                f"--shared_io: {len(members)} {kind} need their own slots but II is {II}"
            )
    return [("enter", inputs), ("exit", outputs)]


def main(argv=None):

    args = parse_args(argv)

    dfg_dir = args.dfg
    II = args.II
    C = args.C
    log_file = args.log
    tag = args.tag
    placement_time_delta = args.place_time
    sched_time = args.sched_time
    schedule_length = args.II
    unroll_factor = args.unroll
    sched_method = args.sched_method
    io_diffusion = args.iod
    arith_diffusion = args.ard
    seed = args.seed
    max_C = args.max_C

    # fixed device flow: PE types and layout come from a device file instead of the DFG
    device_spec = load_device_spec(args.device) if args.device else None
    if C is None:
        C = device_spec.channels if device_spec else 1
    # soft bitstream memories hold II_MAX slots; the programmed II picks how many run
    ii_max = args.ii_max or (device_spec.ii_max if device_spec else None) or II
    assert ii_max >= II, f"II_MAX {ii_max} (--ii_max or the device file) is smaller than -II {II}"
    assert args.cfg_width >= 1, "--cfg_width must be at least 1"
    assert args.data_width >= 1, "--data_width must be at least 1"

    noc_pipelining_stages = args.noc_pipe
    pe_pipelining_stages = args.pe_pipe
    # num of PE outputs
    IO_O = 1
    IO_I = 2
    NUM_OPERANDS = 2

    print("\n\nCGRA-ILP: High-Level Synthesis Compiler for Mocarabe\n\n")
    # user warnings

    class bcolors:
        WARNING = "\033[93m"
        ENDC = "\033[0m"

    if schedule_length != II:
        warnings.warn(f"{bcolors.WARNING}T != II: this is experimental{bcolors.ENDC}")
    if io_diffusion > II:
        warnings.warn(
            f"{bcolors.WARNING}iod > II: trying to pack more input nodes in a PE than the modulo schedule can handle{bcolors.ENDC}"
        )
    if arith_diffusion > II:
        warnings.warn(
            f"{bcolors.WARNING}ard > II: trying to pack more operations in a PE than the modulo schedule can handle{bcolors.ENDC}"
        )

    assert os.path.exists(dfg_dir), (
        f"{os.path.realpath(dfg_dir)} does not exist.  Have you run gcc?"
    )
    assert sched_method == "ILP" or sched_method == "PF", (
        "sched_method must be either 'ILP' or 'PF' "
    )
    assert IO_O > 0 and IO_O <= C, "0 < IO_O <= C must hold"

    """ Environment Setup """
    dfg_dir = dfg_dir.strip("/")
    benchmark_name = os.path.basename(dfg_dir)
    timestamp_suffix = datetime.now().strftime("--%d-%m-%y-%H.%M.%S.%f")
    file_helper = FilePathsHelper("proj/", benchmark_name, timestamp_suffix)
    file_helper.mk_proj_subdirectories()
    file_helper.log_file = log_file

    print("Copying DFG files from hls/ to {}hls/".format(file_helper.proj_dir))
    shutil.copy(
        os.path.join(dfg_dir, benchmark_name + ".hgr"),
        file_helper.hgr_dir + benchmark_name + ".hgr",
    )

    print(
        "Copying verilog files from rtl/rtl-for-sim/ to {}rtl/".format(
            file_helper.proj_dir
        )
    )
    for rtl_file in [
        "pe_mux_2_input.sv",
        "pe_srl.v",
        "pe_2_input.sv",
        "pe_mux_3_input.sv",
        "pe_mux_n_input.sv",
        "cfg_loader.sv",
        "cfg_row.sv",
        "pe_cfg.sv",
        "SRL16E.v",
        "SRLC32E.v",
        "SRL64.v",
        "torus_switch.sv",
        "mocarabe.sv",
        "mocarabe.h",
    ]:
        shutil.copy(
            os.path.join("rtl", "rtl", rtl_file),
            os.path.join(file_helper.proj_dir, "rtl", rtl_file),
        )

    if not os.path.exists("svg"):
        print("Creating 'svg' directory")
        os.makedirs("svg")

    # Deserialize and unroll dataflow hypergraph
    if unroll_factor == 0:
        # If there are fewer than II instances of a given operator, unroll by II
        # This is to keep PE utilization high for small benchmarks
        dataflow_hgraph = Netlist(
            os.path.join(dfg_dir, benchmark_name + ".hgr"),
            unroll_factor=1,
            split_input_fanout=args.split_input_fanout,
        )
        arith_oprtrs = collections.Counter(
            dataflow_hgraph.extract_node_arithmetic_operators().values()
        )
        io_operators = collections.Counter(
            dataflow_hgraph.extract_node_io_operators().values()
        )
        if "+" not in arith_oprtrs:
            arith_oprtrs["+"] = 0
        if "*" not in arith_oprtrs:
            arith_oprtrs["*"] = 0

        if (
            (arith_oprtrs["+"] < II and arith_oprtrs["+"] != 0)
            or (arith_oprtrs["*"] < II and arith_oprtrs["*"] != 0)
            or (io_operators["IO"] < II and io_operators["IO"] != 0)
        ):
            unroll_factor = II
        else:
            unroll_factor = 1

        dataflow_hgraph = Netlist(
            os.path.join(dfg_dir, benchmark_name + ".hgr"),
            unroll_factor,
            split_input_fanout=args.split_input_fanout,
        )
        print(f"Auto-Unroll factor: {unroll_factor}")
    else:
        dataflow_hgraph = Netlist(
            dfg_path=os.path.join(dfg_dir, benchmark_name + ".hgr"),
            unroll_factor=unroll_factor,
            split_input_fanout=args.split_input_fanout,
        )

    write_dot(
        dataflow_hgraph.to_graph(),
        os.path.join(file_helper.dot_dir, benchmark_name + ".dot"),
    )

    if len(dataflow_hgraph.get_node_set()) == 0:
        raise ValueError(f"DFG {dfg_dir} is empty")

    operatorless = dataflow_hgraph.extract_operatorless_nodes()
    if operatorless:
        raise ValueError(
            f"DFG nodes {sorted(set(operatorless.values()))} have two inputs but no "
            "operator; label them with their operator and add a separate output node"
        )

    """ PE Allocation """

    if device_spec:
        if io_diffusion != 1.0 or arith_diffusion != 1.0:
            warnings.warn(
                f"{bcolors.WARNING}-iod/-ard are ignored with --device{bcolors.ENDC}"
            )
        check_dfg_fits(device_spec, dataflow_hgraph, II)
        print(f"Fixed device: {device_spec.name}")
        Nx, Ny, device_map = device_spec.Nx, device_spec.Ny, device_spec.device_map
    else:
        Nx, Ny, device_map = pe_alloc.ClosestFactorsAllocator().allocate_pes(
            dataflow_hgraph, II, io_diffusion, arith_diffusion
        )
    print(f"Nx={Nx}, Ny={Ny}")
    print(pe_alloc.to_string(device_map))
    num_partitions_given_to_operator = collections.Counter(
        np.ndarray.flatten(device_map)
    )

    """ Partitioning/Packing and Placement """
    random.seed(seed)
    placement_start_time = datetime.now()
    partition_filename = (
        file_helper.partition_dir
        + benchmark_name
        + "-K"
        + str(Nx * Ny)
        + "-U"
        + str(unroll_factor)
    )

    dfg_node_to_pe_xy_map_, pe_operators = placr.IlpAndSimulatedAnnealingPlacer().place(
        dataflow_hgraph,
        Nx * Ny,
        num_partitions_given_to_operator,
        partition_filename + ".sol",
        II,
        placement_time_delta,
        Nx,
        Ny,
        file_helper.log_dir,
        seed=seed,
        fixed_device_map=device_map if device_spec else None,
    )
    if device_spec:
        placed_types = [device_map[pe % Nx][pe // Nx] for pe in range(Nx * Ny)]
        assert list(pe_operators) == placed_types, (
            f"placement changed PE types: {pe_operators} != {placed_types}"
        )

    # serialize placement
    file_helper.write_list_to_file(
        file_helper.placement_dir + "dfg_node_to_pe_xy.json", dfg_node_to_pe_xy_map_
    )

    # serialize placed netlist (scheduler input)
    serialized_placed_netlist = placr.serialize_placed_netlist(
        dataflow_hgraph, dfg_node_to_pe_xy_map_, True
    )
    placed_netlist = placr.create_placed_netlist(
        dataflow_hgraph, dfg_node_to_pe_xy_map_, True
    )

    netfile = open(file_helper.netlist_filepath, "w+")
    netfile.write(serialized_placed_netlist)
    netfile.close()

    placement_time_delta = datetime.now() - placement_start_time

    """ Scheduling """
    num_nets = len(dataflow_hgraph.get_hyperedge_id_set())
    file_helper.schedule_filepath = (
        file_helper.schedule_dir
        + benchmark_name
        + "-Nx%d-Ny%d-C%d-num_nets%d-T%d" % (Nx, Ny, C, num_nets, schedule_length)
        + ".sol"
    )

    layout = ""
    device = Device(
        Nx,
        Ny,
        C,
        schedule_length,
        schedule_length,
        IO_I,
        IO_O,
        layout,
        pe_pipelining_stages,
        noc_pipelining_stages,
        unroll_factor,
        num_nets,
        II,
        data_width=args.data_width,
        fifo_depth=args.fifo_depth,
        shared_io=args.shared_io,
    )
    if args.shared_io:
        device.shared_io_groups = shared_io_groups(dataflow_hgraph, dfg_node_to_pe_xy_map_, II)
    if sched_method == "ILP":
        boundingBoxEnabled = False

        scheduled_netlist = schedulr.IlpScheduler().run_scheduling_with_timeout(
            device,
            placed_netlist,
            placement_time_delta,
            file_helper,
            num_partitions_given_to_operator,
            tag,
            sched_time=sched_time,
            seed=seed,
            max_channels=max_C,
        )

        if scheduled_netlist != None:
            """ RTL """
            T = II
            # the scheduler raises C when it cannot find a schedule
            C = device.physical_channels
            print(f"Scheduled with C={C}")

            print("--------------Generating Simulation RTL--------------\n")

            h, v, enter, exit_, T = RTLGenerator.deserialize_schedule(
                file_helper.schedule_filepath,
                Nx,
                Ny,
                device.physical_channels,
                num_nets,
                T,
            )

            RTLGenerator.generate_and_write_noc_mux_memories(
                file_helper.rtl_dir,
                h,
                v,
                enter,
                exit_,
                Nx,
                Ny,
                C,
                num_nets,
                T,
                noc_pipelining_stages,
            )

            """ verify scheduled netlist channel utilization """
            utilization_factor = scheduled_netlist.physical_channel_utilization_factor(
                device.Nx, device.Ny, device.physical_channels, T
            )
            unused_xy = scheduled_netlist.unused_xy(
                device.Nx, device.Ny, device.physical_channels, T
            )

            verilog_header = RTLGenerator.verilog_header_gen(
                file_helper.proj_dir + "rtl/",
                device,
                pe_operators,
                ii_max=ii_max,
                cfg_width=args.cfg_width,
                soft=args.bitstream == "soft",
            )

            verilog_header_filename = file_helper.rtl_dir + "benchmark.h"
            file_helper.write_string_to_file(verilog_header_filename, verilog_header)

            resource_graph = ResourceGraph()
            resource_graph.create(device)

            net_paths = RTLGenerator.get_net_path_nodes(
                dataflow_hgraph, resource_graph, device, h, v, enter, exit_
            )
            op_addresses, op_port_select, asserts_string, latency6 = (
                RTLGenerator.generate_and_write_pe_memories(
                    file_helper.proj_dir,
                    resource_graph,
                    net_paths,
                    dataflow_hgraph,
                    dfg_node_to_pe_xy_map_,
                    enter,
                    exit_,
                    NUM_OPERANDS,
                    IO_I,
                    II,
                    device,
                    h=h,
                    v=v,
                )
            )

            # the soft bitstream packs the same .dat files the hard bitstream loads
            cfg_words = 0
            if C > 1:
                cfg_words = RTLGenerator.write_bitstream(
                    file_helper.rtl_dir, Nx, Ny, C, II, ii_max, args.cfg_width, args.fifo_depth
                )
            elif args.bitstream == "soft":
                raise ValueError("the soft bitstream needs -C 2 or more")

            RTLGenerator.testbench_gen(
                file_helper.proj_dir + "rtl/",
                Nx,
                Ny,
                C,
                asserts_string,
                cfg_words,
                fifo_depth=args.fifo_depth,
                shared_io=args.shared_io,
            )

            Sim.print_vivado_sim_cmd(file_helper)
            Sim.print_iverilog_sim_cmd(file_helper)

            print("\nFor a visualization of the schedule:\n")
            print(
                "python3 mocarabe/torus_gui_freeze.py --proj {} --zoom 5".format(
                    file_helper.proj_dir
                )
            )
            print("\n")

    elif sched_method == "PF":
        warnings.warn(
            f"{bcolors.WARNING} PathFinder scheduler not maintained to the same level as ILP scheduler"
        )
        file_helper.tag = tag
        device.num_partitions_given_to_operator = num_partitions_given_to_operator
        scheduled_netlist = schedulr.PathfinderScheduler().run_scheduling_with_timeout(
            device,
            placed_netlist,
            placement_time_delta,
            file_helper,
            num_partitions_given_to_operator,
            tag,
        )

        print(
            "python3 mocarabe/torus_gui_freeze.py --proj {} --zoom 5".format(
                file_helper.proj_dir
            )
        )
        verilog_header = RTLGenerator.verilog_header_gen(
            file_helper.proj_dir + "rtl/", device, pe_operators
        )
        verilog_header_filename = file_helper.rtl_dir + "benchmark.h"
        file_helper.write_string_to_file(verilog_header_filename, verilog_header)

    return file_helper.rtl_dir


if __name__ == "__main__":
    main()
