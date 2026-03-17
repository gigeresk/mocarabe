import os
import sys


def modify_benchmark_header(path, x, y, c, DW=32, sched_len=4):
    f = open(path + "/benchmark.h", "w")
    f.write(
        """`define BENCHMARK_DATA_WIDTH """
        + str(DW)
        + """
`define D_WIDTH [`BENCHMARK_DATA_WIDTH-1:0]
`define BENCHMARK_X_WIDTH """
        + str(x)
        + """
`define BENCHMARK_Y_WIDTH """
        + str(y)
        + """
`define BENCHMARK_SCHED_LEN """
        + str(sched_len)
        + """
`define BENCHMARK_CHAN_WIDTH """
        + str(c)
    )
    f.close()


def run_mocarabe():
    print(
        "\n\nMocarabe: High-Performance Time-Multiplexed Overlays for FPGAs\n University of Waterloo\n\n"
    )
    if len(sys.argv) > 1:
        x = int(sys.argv[1])
        y = int(sys.argv[2])
        c = int(sys.argv[3])
        batch = int(sys.argv[4])
    else:
        x = 10
        y = 10
        c = 3
        batch = 1
    os.system("python3 placement.py " + str(x) + " " + str(y) + " " + str(c))
    modify_benchmark_header("./rtl", x, y, c)
    if batch == 1:
        print("Launching Vivado in batch mode...")
        os.system("vivado -mode batch -source cgra.tcl")
    else:
        print("Launching Vivado in command line mode...")
        os.system("vivado -mode tcl -source cgra.tcl")


run_mocarabe()
