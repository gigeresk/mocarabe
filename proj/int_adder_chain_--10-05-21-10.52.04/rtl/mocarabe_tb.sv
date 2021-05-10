
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
		$display("#1\n");
	end

    initial begin
        $display("Begin testbench");
        #6 //cycle 6 
        assert( pe_out[0 + 2*1] == 201)  $display("PE (0+2*1) outputting 201 (node 2) @6|  |  |  |  |  |  |  |  ");else $display("Assert error:  pe_out[0+2*1](node 2) == %d @6, should be 201---------------------------------------------",pe_out[0+2*1]);
        #4 //cycle 10 
        assert( pe_out[1 + 2*1] == 305)  $display("PE (1+2*1) outputting 305 (node 1) @10|  |  |  |  |  |  |  |  ");else $display("Assert error:  pe_out[1+2*1](node 1) == %d @10, should be 305---------------------------------------------",pe_out[1+2*1]);
        #13 //cycle 23 
        assert( pe_out[1 + 2*1] == 318)  $display("PE (1+2*1) outputting 318 (node 4) @23|  |  |  |  |  |  |  |  ");else $display("Assert error:  pe_out[1+2*1](node 4) == %d @23, should be 318---------------------------------------------",pe_out[1+2*1]);
        #2 //cycle 25 
        assert( pe_out[1 + 2*2] == 506)  $display("PE (1+2*2) outputting 506 (node 0) @25|  |  |  |  |  |  |  |  ");else $display("Assert error:  pe_out[1+2*2](node 0) == %d @25, should be 506---------------------------------------------",pe_out[1+2*2]);
        #12 //cycle 37 
        assert( pe_out[0 + 2*1] == 232)  $display("PE (0+2*1) outputting 232 (node 6) @37|  |  |  |  |  |  |  |  ");else $display("Assert error:  pe_out[0+2*1](node 6) == %d @37, should be 232---------------------------------------------",pe_out[0+2*1]);
        #1 //cycle 38 
        assert( pe_out[1 + 2*2] == 824)  $display("PE (1+2*2) outputting 824 (node 3) @38|  |  |  |  |  |  |  |  ");else $display("Assert error:  pe_out[1+2*2](node 3) == %d @38, should be 824---------------------------------------------",pe_out[1+2*2]);
        #15 //cycle 53 
        assert( pe_out[0 + 2*2] == 1056)  $display("PE (0+2*2) outputting 1056 (node 5) @53|  |  |  |  |  |  |  |  ");else $display("Assert error:  pe_out[0+2*2](node 5) == %d @53, should be 1056---------------------------------------------",pe_out[0+2*2]);
#10
$finish;

    end

endmodule
