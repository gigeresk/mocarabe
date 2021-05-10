create_project cgra-ilp -f ./cgra-ilp -part xcu280-fsvh2892-2L-e
set_property board_part xilinx.com:au280:part0:1.1 [current_project]

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

read_xdc mapping.xdc
synth_design -generic PE_PIPE=7 -generic PIPENUM=1 -generic PECONFIG=400'h1111111111111101111101001111011110111111111111101111101010111110111111110111111001010111011111010011 -top mocarabe  -mode out_of_context -keep_equivalent_registers -retiming;
opt_design;
place_design;
phys_opt_design;
phys_opt_design -slr_crossing_opt -tns_cleanup;
route_design;
phys_opt_design;
report_utilization -file utilization_report.txt
report_timing -file timing_report.txt
