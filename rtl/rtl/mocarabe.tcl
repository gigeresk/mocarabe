vlib work
vlog +acc -sv mocarabe_tb.v pe_mux_2_input.sv pe_mux_3_input.sv mocarabe.v pe_2_input.sv pe_srl.v torus_switch.sv SRL16E.v SRLC32E.v SRL64.v srl_tb.v
vsim mocarabe_tb
add wave -position insertpoint  sim:/mocarabe_tb/*
add wave  \
{sim:/mocarabe_tb/mocarabe_dut/ys[1]/xs[1]/genblk1/pe_inst/i_operand0} \
{sim:/mocarabe_tb/mocarabe_dut/ys[1]/xs[1]/genblk1/pe_inst/i_operand1}
add wave  \
{sim:/mocarabe_tb/mocarabe_dut/ys[1]/xs[1]/genblk1/pe_inst/result}
config wave -signalnamewidth 1
run 2000 ps
