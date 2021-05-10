
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
        #5 //cycle 5 
        assert( pe_out[0 + 2*1] == 200)  $display("PE (0+2*1) outputting 200 (node 2) @5|  |  |  |  |  |  |  |  ");else $display("Assert error:  pe_out[0+2*1](node 2) == %d @5, should be 200---------------------------------------------",pe_out[0+2*1]);
        #1 //cycle 6 
        assert( pe_out[1 + 2*0] == 101)  $display("PE (1+2*0) outputting 101 (node 1) @6|  |  |  |  |  |  |  |  ");else $display("Assert error:  pe_out[1+2*0](node 1) == %d @6, should be 101---------------------------------------------",pe_out[1+2*0]);
        #13 //cycle 19 
        assert( pe_out[1 + 2*0] == 114)  $display("PE (1+2*0) outputting 114 (node 4) @19|  |  |  |  |  |  |  |  ");else $display("Assert error:  pe_out[1+2*0](node 4) == %d @19, should be 114---------------------------------------------",pe_out[1+2*0]);
        #2 //cycle 21 
        assert( pe_out[1 + 2*1] == 301)  $display("PE (1+2*1) outputting 301 (node 0) @21|  |  |  |  |  |  |  |  ");else $display("Assert error:  pe_out[1+2*1](node 0) == %d @21, should be 301---------------------------------------------",pe_out[1+2*1]);
        #13 //cycle 34 
        assert( pe_out[1 + 2*1] == 415)  $display("PE (1+2*1) outputting 415 (node 3) @34|  |  |  |  |  |  |  |  ");else $display("Assert error:  pe_out[1+2*1](node 3) == %d @34, should be 415---------------------------------------------",pe_out[1+2*1]);
        #4 //cycle 38 
        assert( pe_out[0 + 2*1] == 233)  $display("PE (0+2*1) outputting 233 (node 6) @38|  |  |  |  |  |  |  |  ");else $display("Assert error:  pe_out[0+2*1](node 6) == %d @38, should be 233---------------------------------------------",pe_out[0+2*1]);
        #15 //cycle 53 
        assert( pe_out[0 + 2*2] == 648)  $display("PE (0+2*2) outputting 648 (node 5) @53|  |  |  |  |  |  |  |  ");else $display("Assert error:  pe_out[0+2*2](node 5) == %d @53, should be 648---------------------------------------------",pe_out[0+2*2]);
#10
$finish;

    end

endmodule
