# defaults for Device.data_width (PE datapath bits; expected values wrap at this
# width) and Device.fifo_depth (operands wait at most FIFO_DEPTH - 1 cycles)
DATA_WIDTH = 32
FIFO_DEPTH = 64
# depths pe_srl.v implements (Xilinx SRL16E/SRLC32E/SRL64 models)
FIFO_DEPTHS = (16, 32, 64)


def verilog_header_gen(rtl_dir, device, pe_operators, ii_max=None, cfg_width=1, soft=False):
    """soft picks the default bitstream (BITSTREAM_SOFT, overridable with
    -DBITSTREAM_SOFT=0|1); ii_max sizes the soft bitstream's schedule memories."""
    # //eg:
    # `define BENCHMARK_DATA_WIDTH 32
    # `define BENCHMARK_X_WIDTH 3
    # `define BENCHMARK_Y_WIDTH 3
    # `define BENCHMARK_SCHED_LEN 8
    # `define peconf 9'b001001001

    result = "// Application-specific macro parameters\n"
    result += f"`define BENCHMARK_DATA_WIDTH {device.data_width}\n"
    result += f"`define BENCHMARK_X_WIDTH {device.Nx}\n"
    result += f"`define BENCHMARK_Y_WIDTH {device.Ny}\n"
    result += f"`define BENCHMARK_SCHED_LEN {device.II}\n"
    result += f"`define BENCHMARK_CHAN_WIDTH {device.physical_channels}\n"
    result += f"`define FIFO_DEPTH {device.fifo_depth}\n"
    result += f"`define BENCHMARK_II_MAX {ii_max or device.II}\n"
    result += f"`define CFG_WIDTH {cfg_width}\n"
    result += "`ifndef BITSTREAM_SOFT\n"
    result += f"`define BITSTREAM_SOFT {int(soft)}\n"
    result += "`endif\n"
    result += (
        f"`define TORUS_SWITCH_PIPE_NUM  {int(device.noc_pipelining_stages) - 1}\n"
    )
    result += f"`define PE_PIPE_NUM {device.pe_pipelining_stages}"
    result += """//adder and u=multiplier configuration
    //must be modified for each configuration, with a bit for each pe. 0 is for an adder, and 1 is for a multiplier.the config bits are input from right to left, with the lsb being the
    //pe at top left, and msb being the pe at bottom right
    """

    pe_id_to_operator = ["0"] * (device.Nx * device.Ny)

    for ix, op in enumerate(pe_operators):
        if op == "*":
            pe_id_to_operator[ix] = "1"
        elif op == "+":
            pe_id_to_operator[ix] = "0"
        elif op in ("IN", "OUT", "IO"):
            pe_id_to_operator[ix] = "2"
        else:
            pe_id_to_operator[ix] = "3"
    pe_id_to_operator.reverse()
    peconf = "".join(pe_id_to_operator)
    result = (
        result
        + """
//adder and u=multiplier configuration
//must be modified for each configuration, with a bit for each pe. 0 is for an adder, and 1 is for a multiplier.the config bits are input from right to left, with the lsb being the
//pe at top left, and msb being the pe at bottom right
"""
    )
    result += f"`define PECONF {4 * device.Nx * device.Ny}'h{peconf}\n"
    # for pe_operator in pe_id_to_operator[1:]:
    #     result += f",{pe_operator} "

    f = open(f"{rtl_dir}/benchmark.h", "w+")
    f.write(result)

    return result
