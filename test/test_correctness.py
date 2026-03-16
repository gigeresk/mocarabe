# Tests to ensure that simulations are running correctly


def test_correctness(dfg, iod, ard, ii, c, place_time, sched_method):
    
    
    # python3 mocarabe.py -dfg hgr/int_poly3 -iod 1 -ard 1 -II 1 -C 20 --place_time 0.1 --sched_method ILP
    
    # iverilog -g2012 -o mocarabe_sim.vvp mocarabe.sv pe_2_input.sv torus_switch.sv pe_srl.v pe_mux_2_input.sv pe_mux_3_input.sv SRL16E.v SRLC32E.v SRL64.v mocarabe_tb.sv
    
    # vvp mocarabe_sim.vvp
    
    #     python3 mocarabe.py -dfg hgr/int_adder_chain -iod 1 -ard 1 -II 1 -C 20 --place_time 0.1 --sched_method ILP
    # python3 mocarabe.py -dfg hgr/int_adder_chain -iod 1 -ard 1 -II 2 -C 20 --place_time 0.1 --sched_method ILP
    # python3 mocarabe.py -dfg hgr/int_adder_chain -iod 1 -ard 1 -II 3 -C 20 --place_time 0.1 --sched_method ILP
    pass