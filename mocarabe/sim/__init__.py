class Sim:
    def print_vivado_sim_cmd(file_helper):
        print("\nTo start a simultation with xsim (Vivado simulator):\n")
        print(f"cd {file_helper.proj_dir}/rtl/")
        print(
            "xvlog --sv mocarabe.sv pe_2_input.sv torus_switch.sv pe_srl.v pe_mux_2_input.sv pe_mux_3_input.sv SRL16E.v SRLC32E.v SRL64.v mocarabe_tb.sv"
        )
        print("xelab -debug typical mocarabe_tb -s mocarabe_sim")
        print("xsim mocarabe_sim")

    def print_iverilog_sim_cmd(file_helper):
        print("\nTo start a simultation with iverilog:\n")
        print(f"cd {file_helper.proj_dir}/rtl/")
        print(
            "iverilog -g2012 -o mocarabe_sim.vvp mocarabe.sv pe_2_input.sv torus_switch.sv pe_srl.v pe_mux_2_input.sv pe_mux_3_input.sv SRL16E.v SRLC32E.v SRL64.v mocarabe_tb.sv"
        )
        print("vvp mocarabe_sim.vvp")
        # print("xsim mocarabe_sim")
