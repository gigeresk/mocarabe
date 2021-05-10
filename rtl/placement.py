import sys

#This script generates an xdc constraint file to be used by Vivado


#write the xdc file to place the design on the Xilinx U280 board, setting a target frequency of 1GHz
def write_xdc(x = 19, y = 69, num_channel = 3, p = 2, name = "mapping.xdc"):#p = number of pipeline registers for torus_switch
    for pe_y in range(10, 11):#modify for different PE sizes
        for pe_x in range(10, 11):#modify for different PE sizes
            if pe_y * pe_x <= 100:#checking if PE size is less than 100. Can be removed.

                f = open(name, "w")
                f.write(
                    "create_clock -period 1.000 -name clk -waveform {0.000 0.500 } [get_ports clk]\n\n\n")  # edit this to modify frequency
                xtop = x - 1
                ytop = y - 1
                ybot = 0
                xbot = 0
                xbase = 16 #placement offset
                ybase = 20 #placement offset

                # place = [0, 9, 1, 8, 2, 7, 3, 6, 4, 5]   # Placement order. The current order is optimized for torus.

                for i in range(x):
                    ytop = y - 1
                    ybot = 0
                    f.write("#col number " + str(i) + "\n")
                    if i % 2 == 0:
                        cur_x = xbot
                        xbot = xbot + 1
                    else:
                        cur_x = xtop
                        xtop = xtop - 1
                    for j in range(y):
                        if j % 2 == 0:
                            cur_y = ybot
                            ybot = ybot + 1
                        else:
                            cur_y = ytop
                            ytop = ytop - 1
                        f.write("create_pblock y" + str(cur_y) + "x" + str(cur_x) + "\n")
                        #single channel, no fanin muxes needed
                        if num_channel == 1:
                            f.write(
                                "add_cells_to_pblock [get_pblocks y" + str(cur_y) + "x" + str(
                                    cur_x) + "] [get_cells -quiet [list {ys[" + str(
                                    cur_y) + "].xs[" + str(cur_x) + "].torus_switch_inst} {ys[" + str(
                                    cur_y) + "].xs[" + str(
                                    cur_x) + "].pe_inst}]]\n")
                        else: 
                            for chan in range(0, num_channel):
                                if chan == 0:
                                    f.write(
                                        "add_cells_to_pblock [get_pblocks y" + str(cur_y) + "x" + str(
                                            cur_x) + "] [get_cells -quiet [list {ys[" + str(
                                            cur_y) + "].xs[" + str(cur_x) + "].cs[" + str(chan) + "].torus_switch_inst} {ys[" + str(
                                            cur_y) + "].xs[" + str(
                                            cur_x) + "].pe_inst}]]\n")
                                    f.write(
                                        "add_cells_to_pblock [get_pblocks y" + str(cur_y) + "x" + str(
                                            cur_x) + "] [get_cells -quiet [list {ys[" + str(
                                            cur_y) + "].xs[" + str(
                                            cur_x) + "].mux_inst}]]\n")

                                else:
                                    f.write("add_cells_to_pblock [get_pblocks y" + str(cur_y) + "x" + str(
                                        cur_x) + "] [get_cells -quiet [list {ys[" + str(
                                        cur_y) + "].xs[" + str(cur_x) + "].cs[" + str(chan) + "].torus_switch_inst}]]\n")
                            
                        f.write(
                            "resize_pblock [get_pblocks y" + str(cur_y) + "x" + str(
                                cur_x) + "] -add {SLICE_X" + str(
                                xbase + i * pe_x) + "Y" + str(
                                ybase + j * pe_y) + ":SLICE_X" + str(xbase + (i + 1) * pe_x - 1) + "Y" + str(
                                ybase + (j + 1) * pe_y - 1) + "}\n")
                        if (19 < j < 24) or (43 < j < 48):  # to use laguna registers for crossing SLRs
                            for chan in range(0, num_channel):
                                f.write("set_property USER_SLL_REG 1 [get_cells {ys[" + str(
                                    cur_y) + "].xs[" + str(cur_x) + "].cs[" + str(chan) + "].torus_switch_inst/n_out_r_reg["
                                                                                        "*]}]\n")
                                f.write("set_property USER_SLL_REG 1 [get_cells {ys[" + str(
                                    cur_y) + "].xs[" + str(cur_x) + "].cs[" + str(
                                    chan) + "].torus_switch_inst/o_to_pe_r_reg[*]}]\n")
                                f.write("set_property USER_SLL_REG 1 [get_cells {ys[" + str(
                                    cur_y) + "].xs[" + str(cur_x) + "].cs[" + str(
                                    chan) + "].torus_switch_inst/e_out_r_reg[*]}]\n")
                                f.write("set_property USER_SLL_REG 1 [get_cells {ys[" + str(
                                    cur_y) + "].xs[" + str(cur_x) + "].cs[" + str(
                                    chan) + "].torus_switch_inst/s_in_reg_reg[*]}]\n")
                                f.write("set_property USER_SLL_REG 1 [get_cells {ys[" + str(
                                    cur_y) + "].xs[" + str(cur_x) + "].cs[" + str(
                                    chan) + "].torus_switch_inst/w_in_reg_reg[*]}]\n")
                                f.write("set_property USER_SLL_REG 1 [get_cells {ys[" + str(
                                    cur_y) + "].xs[" + str(cur_x) + "].cs[" + str(
                                    chan) + "].torus_switch_inst/i_from_pe_reg_reg[*]}]\n")
                                for p_var in range(p):
                                    f.write("set_property USER_SLL_REG 1 [get_cells {ys[" + str(
                                        cur_y) + "].xs[" + str(cur_x) + "].cs[" + str(chan) + "].torus_switch_inst"
                                                                                            "/genblk1["+str(p_var)+"].n_out_pipe_reg[" + str(
                                        p_var) + "][*]}]\n")
                                    f.write("set_property USER_SLL_REG 1 [get_cells {ys[" + str(
                                        cur_y) + "].xs[" + str(cur_x) + "].cs[" + str(chan) + "].torus_switch_inst"
                                                                                            "/genblk1["+str(p_var)+"].e_out_pipe_reg[" + str(
                                        p_var) + "][*]}]\n")
                                    f.write("set_property USER_SLL_REG 1 [get_cells {ys[" + str(
                                        cur_y) + "].xs[" + str(cur_x) + "].cs[" + str(chan) + "].torus_switch_inst"
                                                                                            "/genblk1["+str(p_var)+"].o_to_pe_pipe_reg[" + str(
                                        p_var) + "][*]}]\n")
                            f.write("set_property gridtypes {DSP48E2 SLICE} [get_pblocks y" + str(cur_y) + "x" + str(
                                cur_x) + "]\n")
                        else:
                            f.write("set_property gridtypes {DSP48E2 SLICE} [get_pblocks y" + str(cur_y) + "x" + str(
                                cur_x) + "]\n")

                        # f.write("add_cells_to_pblock [get_pblocks pblock_dsp] [get_cells g_dsp_true1.U21/* -filter {
                        # REF_NAME == DSP48E1}]")
                        f.write(
                            "add_cells_to_pblock [get_pblocks y" + str(cur_y) + "x" + str(
                                cur_x) + "] [get_cells ys[" + str(
                                cur_y) + "].xs[" + str(cur_x) + "].pe_inst/* -filter {REF_NAME == DSP48E2}]\n")
                        f.write("\n")
                    f.write("\n\n")
                f.close()

#generate the xdc file based on the input arguments
def generate_xdc():
    if len(sys.argv) == 1:  #default mode
        print("Generating XDC with default parameters, x = 19, y = 69, num_channel = 3")
        write_xdc()
    elif len(sys.argv) > 6 or len(sys.argv) < 4:  
        print("Too many/few input parameters. Exiting....")
        exit()  
    else:
        x = int(sys.argv[1])
        y = int(sys.argv[2])
        c = int(sys.argv[3])
        if c == 3:
            p = 2
        else:
            p = 1
        if x < 1 or x > 19 or y < 1 or y > 69 or c < 1 or c > 3:
            print("Input parameters are out of their legal range. Exiting...")
            exit()
        else:
            if len(sys.argv) == 5:
                name = sys.argv[4]+".xdc"
                print("Generating XDC with the following parameters: x =",x,", y =", y, ", num_channel =",c,"output file:", name)
                write_xdc(x, y, c, p, name)
            else:
                print("Generating XDC with the following parameters: x =",x,", y =", y,", num_channel =",c)
                write_xdc(x, y, c, p)


generate_xdc()

