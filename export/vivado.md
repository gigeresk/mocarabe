**CGRA implementation and floorplanning in Vivado**

We implement the Mocarabe overlay using parametric Verilog for PEs and  switches. We  use  Xilinx Vivado 2020.1 tosynthesize, place, and route the design on a Xilinx Alveo U280 card for analysis. We design hand-crafted placement scripts to effectively map the design and make use of FPGA resources while keeping the operation frequency high. Each logical block containing PE and switches is assigned to a physical block(Pblock) on the chip. We define an arbitrary estimate for eachPblock’s size as the number of logic slices  it contains, with each slice containing Look-Up Tables (LUTs) and flip flops.For instance, a 10×10 Pblock  can span the chip from slice X0Y0 to slice X9Y9, creating a rectangular area over the device that contains 100 slices.

The current implementation supports up to three communication channels and the array size of up to 19 x 69. The figure below shows a device oview of a 19 x 69 array with 2 communication channels in Vivado.

![](pics/device.png)

To run implementation, you would need a tcl script and a placement xdc file. There are tcl scripts and placement files provided in the rtl folder. To run Vivado using the tcl script (named cgra.tcl), go to the rtl folder and use the following command:
```bash
#this would open Vivado in command line mode
vivao -mode tcl -source cgra.tcl
```

Depending on the configuration, this could take several (>10) hours. The resulting frequency and resource usage can be found at the timing and utilization reports produced by the tcl file.

In short, a tcl script should look like this:

```tcl
#Create project
create_project cgra-ilp -f ./cgra-ilp -part xcu280-fsvh2892-2L-e
set_property board_part xilinx.com:au280:part0:1.1 [current_project]

#Add files
read_verilog rtl/mocarabe.v
read_verilog rtl/pe_srl.v
read_verilog -sv rtl/torus_switch.sv
read_verilog rtl/mocarabe.h
read_verilog rtl/benchmark.h
read_verilog -sv rtl/pe_2_input.sv
read_verilog -sv rtl/pe_1_input.sv
read_verilog -sv rtl/pe_mux_2_input.sv
read_verilog -sv rtl/pe_mux_3_input.sv
read_verilog rtl/SRL16E.v
read_verilog rtl/SRLC32E.v
read_verilog rtl/SRL64.v

#Read the xdc file
read_xdc mapping.xdc

#Synthesize design
#generics:
# PE_PIPE: Pe pipeline stages (dependant on number of channels)
# PIPENUM: Torous switch output pipeline stages
# PECONFIG: Array configuration. For each PE, 1 = multiplier and 0 = adder. The config bits are input from right to left, with the lsb being the pe at top left, and msb being the pe at bottom right. You can modify it to suit your configuration. Here, 9 is the array size.
synth_design -generic PE_PIPE=7 -generic PIPENUM=1 -generic PECONFIG=36'h101011001 -top mocarabe  -mode out_of_context -keep_equivalent_registers -retiming;
opt_design;
place_design;
phys_opt_design;
phys_opt_design -slr_crossing_opt -tns_cleanup;
route_design;
phys_opt_design;
report_utilization -file utilization_report.txt
report_timing -file timing_report.txt

```

A placement script should look like this:

```bash
create_clock -period 1.000 -name clk -waveform {0.000 0.500 } [get_ports clk]

#create a pblock for each logick block (PE + NoC routers)
#col number 0
create_pblock y0x0
add_cells_to_pblock [get_pblocks y0x0] [get_cells -quiet [list {ys[0].xs[0].cs[0].torus_switch_inst} {ys[0].xs[0].pe_inst}]]
add_cells_to_pblock [get_pblocks y0x0] [get_cells -quiet [list {ys[0].xs[0].mux_inst}]]
add_cells_to_pblock [get_pblocks y0x0] [get_cells -quiet [list {ys[0].xs[0].cs[1].torus_switch_inst}]]
add_cells_to_pblock [get_pblocks y0x0] [get_cells -quiet [list {ys[0].xs[0].cs[2].torus_switch_inst}]]
resize_pblock [get_pblocks y0x0] -add {SLICE_X16Y20:SLICE_X25Y29}
set_property gridtypes {DSP48E2 SLICE} [get_pblocks y0x0]
add_cells_to_pblock [get_pblocks y0x0] [get_cells ys[0].xs[0].pe_inst/* -filter {REF_NAME == DSP48E2}]
.
.
.
```

More information about the rtl code, tcl, and xdc file can be found in the rtl folder.

**Vivado HLS**

To run Vivado HLS for our benchmarks, you can go to the `hls` folder. There is a separate folder for each benchmark containing all the files and scripts needed to run the benchmark. To run each benchmark, you should run the `main.sh` script with the appropriate arguments. This is how you should run `main.sh`:

```bash
  ./main.sh benchmark_name unroll_factor json_file_containing_number_of_operators id target_frequency(700 MHz) target_ii

  #for instance, running for int_adder_chain with unroll factor of 170, operators located in ops.json, id of 700, and targetting ii=1 you should use the following command in the hls/int_adder_chain folder:
  # ./main.sh int_adder_chain 170 ops.json 510 700 1
```
‍‍We define `id` to be (unroll factor * number of operators). Unroll factor, number of operators, and id are unique for each benchmark and target ii. `iiunrolls.csv` located in hls folder contains information about parameters for each benchmark.

Once `main.sh` is finished, you can use `get_results.sh` to extract results and put them into `results.txt` in the same directory. This is what a results file would look like:

```bash
  adder_chain
  int_adder_chain_170_680_700
  results/int_adder_chain_170_680_700/solution1/syn/report/int_adder_chain_csynth.rpt
  BENCH, UNROLL_FACTOR, LUTs, FF, DSP, BRAM,FREQ, Latency, II,
  int_adder_chain, 170, 16349, 38132, 0, 0, 2.984,
  +  Latency:
    * Summary:
    +---------+---------+-----------+-----------+-----+-----+---------+
    |  Latency (cycles) |   Latency (absolute)  |  Interval | Pipeline|
    |   min   |   max   |    min    |    max    | min | max |   Type  |
    +---------+---------+-----------+-----------+-----+-----+---------+
    |       12|       12| 17.148 ns | 17.148 ns |   12|   12|   none  |
    +---------+---------+-----------+-----------+-----+-----+---------+

  --
        |          |  Latency (cycles) | Iteration|  Initiation Interval  | Trip |          |
        | Loop Name|   min   |   max   |  Latency |  achieved |   target  | Count| Pipelined|
        +----------+---------+---------+----------+-----------+-----------+------+----------+
        |- loop1   |       10|       10|         5|          1|          1|     6|    yes   |
        +----------+---------+---------+----------+-----------+-----------+------+----------+
```

For each benchmark run, you can run `get_results.sh` using the following input arguments:

```bash
  ./get_results.sh benchmark_name unroll_factor id target_frequency
```

There are operator json files and scripts to run each benchmark for tarhetting ii 1-5 in each benchmark folder. You can either limit Vivado HLS to use the same number of operators as Mocarabe does (`run.sh`) or run Vivado HLS unconstrained so it can use as many operators as it wants.

Furthermore, there are sweep scripts `sweep.sh` and `sweep_unconstrained.sh` in hls folder to run a sweep of all benchmarks using gnu parallel (https://www.gnu.org/software/parallel/).






