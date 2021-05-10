
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
        assert( pe_out[1 + 2*0] == 101)  $display("PE (1+2*0) outputting 101 (node 1) @6|  |  |  |  |  |  |  |  ");else $display("Assert error:  pe_out[1+2*0](node 1) == %d @6, should be 101---------------------------------------------",pe_out[1+2*0]);
        assert( pe_out[0 + 2*1] == 201)  $display("PE (0+2*1) outputting 201 (node 2) @6|  |  |  |  |  |  |  |  ");else $display("Assert error:  pe_out[0+2*1](node 2) == %d @6, should be 201---------------------------------------------",pe_out[0+2*1]);
        #13 //cycle 19 
        assert( pe_out[1 + 2*0] == 114)  $display("PE (1+2*0) outputting 114 (node 4) @19|  |  |  |  |  |  |  |  ");else $display("Assert error:  pe_out[1+2*0](node 4) == %d @19, should be 114---------------------------------------------",pe_out[1+2*0]);
        #3 //cycle 22 
        assert( pe_out[1 + 2*1] == 302)  $display("PE (1+2*1) outputting 302 (node 0) @22|  |  |  |  |  |  |  |  ");else $display("Assert error:  pe_out[1+2*1](node 0) == %d @22, should be 302---------------------------------------------",pe_out[1+2*1]);
        #11 //cycle 33 
        assert( pe_out[0 + 2*1] == 228)  $display("PE (0+2*1) outputting 228 (node 6) @33|  |  |  |  |  |  |  |  ");else $display("Assert error:  pe_out[0+2*1](node 6) == %d @33, should be 228---------------------------------------------",pe_out[0+2*1]);
        #2 //cycle 35 
        assert( pe_out[1 + 2*1] == 416)  $display("PE (1+2*1) outputting 416 (node 3) @35|  |  |  |  |  |  |  |  ");else $display("Assert error:  pe_out[1+2*1](node 3) == %d @35, should be 416---------------------------------------------",pe_out[1+2*1]);
        #16 //cycle 51 
        assert( pe_out[1 + 2*2] == 644)  $display("PE (1+2*2) outputting 644 (node 5) @51|  |  |  |  |  |  |  |  ");else $display("Assert error:  pe_out[1+2*2](node 5) == %d @51, should be 644---------------------------------------------",pe_out[1+2*2]);
#10
$finish;

    end

endmodule
