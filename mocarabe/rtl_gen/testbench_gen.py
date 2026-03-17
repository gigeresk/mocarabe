def testbench_gen(rtl_dir, Nx, Ny, C, asserts_string):

    # Build per-PE io_data assigns: matches the formula in pe_memory_gen assertion values
    io_assigns = ""
    for y in range(Ny):
        for x in range(Nx):
            pe_idx = x + y * Nx
            base = 100 * pe_idx
            io_assigns += f"    assign io_data[{pe_idx}] = {base} + tb_cycle;\n"

    top = f"""
`include "benchmark.h"
`include "mocarabe.h"

module mocarabe_tb #(
	localparam D_W		= `BENCHMARK_DATA_WIDTH,
	localparam X_MAX	= `BENCHMARK_X_WIDTH,
	localparam Y_MAX	= `BENCHMARK_Y_WIDTH
	);

	reg clk;
	reg rst;

    wire `D_WIDTH pe_out `XY;

	wire `D_WIDTH pe_in0 `XY;
	wire `D_WIDTH pe_in1 `XY;

    wire done_pe;
    wire done_all;

    integer fail_count = 0;

    // IO PE stimulus: tb_cycle drives each IO PE's io_input via io_data
    reg [31:0] tb_cycle = 0;
    wire `D_WIDTH io_data `XY;
{io_assigns}
	initial begin
		clk = 0;
		rst = 0;
	end

	mocarabe #(
		.X_MAX(X_MAX), .Y_MAX(Y_MAX))
		p(.clk(clk), .rst(rst), .io_data_in(io_data), .pe_o(pe_out), .pe_input0_o(pe_in0), .pe_input1_o(pe_in1), .done_pe(done_pe), .done_all(done_all));

    always begin
		clk = ~clk;
		#0.5;
	end

    // Increment on negedge so tb_cycle is stable before the next posedge.
    // The posedge clock-gen always block fires at t=0 (before the testbench's
    // own @(posedge clk) blocks arm), so negedge-clocking avoids the off-by-one.
    always @(negedge clk) begin
        tb_cycle <= tb_cycle + 1;
    end

	always begin
		#1
		$display("#1\\n");
	end

    initial begin
        $display("Begin testbench");
"""
    # asserts go here

    end_string = """
    end

endmodule
"""

    f = open(f"{rtl_dir}/mocarabe_tb.sv", "w+")
    f.write(top + asserts_string + end_string)

    return top + asserts_string + end_string
