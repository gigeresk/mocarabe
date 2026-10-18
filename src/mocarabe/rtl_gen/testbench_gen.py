import os

from .header_gen import FIFO_DEPTH


def flush_cycles(fifo_depth=FIFO_DEPTH):
    """Prologue cycles after configuration with rst held and IO inputs at 0: long
    enough to push zeros through every SRL FIFO and pipeline, so both bitstreams
    start run cycle 0 from the same all-zero state."""
    return 2 * fifo_depth + 16


def testbench_gen(
    rtl_dir, Nx, Ny, C, asserts_string, cfg_words=0, fifo_depth=FIFO_DEPTH, shared_io=False
):
    """cfg_words: length of bitstream.hex, streamed in when BITSTREAM_SOFT is 1.
    shared_io: every IO PE reads io_stream.hex (one input bus) instead of its own
    100*pe + cycle formula."""

    # Build per-PE io_data assigns: matches the values in pe_memory_gen's assertions
    io_assigns = ""
    if shared_io:
        with open(os.path.join(rtl_dir, "io_stream.hex")) as f:
            stream_len = len(f.read().split())
        io_assigns += f"    reg `D_WIDTH io_stream [0:{stream_len - 1}];\n"
        io_assigns += '    initial $readmemh("io_stream.hex", io_stream);\n'
        io_assigns += f"    wire `D_WIDTH io_bus = (rst || tb_cycle > {stream_len - 1}) ? 0 : io_stream[tb_cycle];\n"
    for y in range(Ny):
        for x in range(Nx):
            pe_idx = x + y * Nx
            base = 100 * pe_idx
            if shared_io:
                io_assigns += f"    assign io_data[{pe_idx}] = io_bus;\n"
            else:
                io_assigns += f"    assign io_data[{pe_idx}] = rst ? 0 : {base} + tb_cycle;\n"

    top = f"""
`include "benchmark.h"
`include "mocarabe.h"

module mocarabe_tb #(
	localparam D_W		= `BENCHMARK_DATA_WIDTH,
	localparam X_MAX	= `BENCHMARK_X_WIDTH,
	localparam Y_MAX	= `BENCHMARK_Y_WIDTH
	);

	reg clk;
	reg rst = 1;

    wire [X_MAX*Y_MAX-1:0][D_W-1:0] pe_out;
    wire [X_MAX*Y_MAX-1:0][D_W-1:0] pe_in0;
    wire [X_MAX*Y_MAX-1:0][D_W-1:0] pe_in1;
    wire `D_WIDTH io_out;
    wire io_out_valid;

    wire done_pe;
    wire done_all;

    integer fail_count = 0;

    // IO PE stimulus: tb_cycle drives each IO PE's io_input via io_data
    reg [31:0] tb_cycle = 0;
    wire [X_MAX*Y_MAX-1:0][D_W-1:0] io_data;
{io_assigns}
    // Prologue: rst held and IO inputs at 0.  The soft bitstream is streamed in
    // first (one CFG_WIDTH-bit word per clock on cfg_data while cfg_en is high),
    // then FLUSH cycles clear every FIFO and pipeline.  rst drops on a negedge, so
    // the next posedge is run cycle 0.
    localparam SOFT = `BITSTREAM_SOFT;
    localparam CFG_WORDS = {max(cfg_words, 1)};
    localparam PROLOGUE = (SOFT ? CFG_WORDS : 0) + {flush_cycles(fifo_depth)};
    reg cfg_en = 0;
    reg [`CFG_WIDTH-1:0] cfg_data = 0;
    reg [`CFG_WIDTH-1:0] cfg_stream [0:CFG_WORDS-1];
    integer cfg_index = 0;
    integer prologue_left = PROLOGUE;

	initial begin
		clk = 0;
		if (SOFT)
			$readmemh("bitstream.hex", cfg_stream);
	end

	mocarabe #(
		.X_MAX(X_MAX), .Y_MAX(Y_MAX))
		p(.clk(clk), .rst(rst), .cfg_en(cfg_en), .cfg_data(cfg_data), .io_data_in(io_data), .io_out(io_out), .io_out_valid(io_out_valid), .pe_o(pe_out), .pe_input0_o(pe_in0), .pe_input1_o(pe_in1), .done_pe(done_pe), .done_all(done_all));

    always begin
		clk = ~clk;
		#0.5;
	end

    always @(negedge clk) begin
        if (SOFT && cfg_index < CFG_WORDS) begin
            cfg_en <= 1;
            cfg_data <= cfg_stream[cfg_index];
            cfg_index <= cfg_index + 1;
        end else begin
            cfg_en <= 0;
            cfg_data <= 0;
        end
        if (prologue_left > 0)
            prologue_left <= prologue_left - 1;
        else
            rst <= 0;
    end

    // Increment on negedge so tb_cycle is stable before the next posedge.
    // The posedge clock-gen always block fires at t=0 (before the testbench's
    // own @(posedge clk) blocks arm), so negedge-clocking avoids the off-by-one.
    always @(negedge clk) begin
        if (rst)
            tb_cycle <= 0;
        else
            tb_cycle <= tb_cycle + 1;
    end

`ifdef TRACE
    // Cycle-by-cycle trace of every PE's output and operand inputs, from run cycle 0
    integer trace_fd;
    integer trace_pe;
    initial trace_fd = $fopen("trace.txt", "w");
    always @(posedge clk) begin
        if (!rst) begin
            $fwrite(trace_fd, "%0d", tb_cycle);
            for (trace_pe = 0; trace_pe < X_MAX*Y_MAX; trace_pe = trace_pe + 1)
                $fwrite(trace_fd, " %0d,%0d,%0d", pe_out[trace_pe], pe_in0[trace_pe], pe_in1[trace_pe]);
            $fwrite(trace_fd, "\\n");
        end
    end
`endif

	always begin
		#1
		$display("#1\\n");
	end

    initial begin
        $display("Begin testbench");
        // assertion times below count from run cycle 0
        wait (rst == 0);
        @(posedge clk);
"""
    # asserts go here

    end_string = """
    end

endmodule
"""

    f = open(f"{rtl_dir}/mocarabe_tb.sv", "w+")
    f.write(top + asserts_string + end_string)

    return top + asserts_string + end_string
