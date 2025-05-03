def testbench_gen(rtl_dir, Nx, Ny, C, asserts_string):

    top = \
        '''
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

	initial begin
		clk = 0;
		rst = 0;
	end

	mocarabe #(
		.X_MAX(X_MAX), .Y_MAX(Y_MAX))
		p(.clk(clk), .rst(rst), .pe_o(pe_out), .pe_input0_o(pe_in0), .pe_input1_o(pe_in0), .done_pe(done_pe), .done_all(done_all));

    always begin
		clk = ~clk;
		#0.5;
	end

	always begin
		#1
		$display("#1\\n");
	end

    initial begin
        $display("Begin testbench");
'''
    # asserts go here

    end_string = \
        '''
    end

endmodule
'''

    f = open(f"{rtl_dir}/mocarabe_tb.sv", "w+")
    f.write(top + asserts_string + end_string)

    return top + asserts_string + end_string
