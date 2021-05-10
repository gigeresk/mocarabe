
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
        #1 //cycle 7 
        assert( pe_out[1 + 2*0] == 102)  $display("PE (1+2*0) outputting 102 (node 1) @7|  |  |  |  |  |  |  |  ");else $display("Assert error:  pe_out[1+2*0](node 1) == %d @7, should be 102---------------------------------------------",pe_out[1+2*0]);
        #13 //cycle 20 
        assert( pe_out[1 + 2*0] == 115)  $display("PE (1+2*0) outputting 115 (node 4) @20|  |  |  |  |  |  |  |  ");else $display("Assert error:  pe_out[1+2*0](node 4) == %d @20, should be 115---------------------------------------------",pe_out[1+2*0]);
        #2 //cycle 22 
        assert( pe_out[1 + 2*1] == 303)  $display("PE (1+2*1) outputting 303 (node 0) @22|  |  |  |  |  |  |  |  ");else $display("Assert error:  pe_out[1+2*1](node 0) == %d @22, should be 303---------------------------------------------",pe_out[1+2*1]);
        #13 //cycle 35 
        assert( pe_out[1 + 2*1] == 418)  $display("PE (1+2*1) outputting 418 (node 3) @35|  |  |  |  |  |  |  |  ");else $display("Assert error:  pe_out[1+2*1](node 3) == %d @35, should be 418---------------------------------------------",pe_out[1+2*1]);
        #2 //cycle 37 
        assert( pe_out[0 + 2*1] == 232)  $display("PE (0+2*1) outputting 232 (node 6) @37|  |  |  |  |  |  |  |  ");else $display("Assert error:  pe_out[0+2*1](node 6) == %d @37, should be 232---------------------------------------------",pe_out[0+2*1]);
        #16 //cycle 53 
        assert( pe_out[0 + 2*2] == 650)  $display("PE (0+2*2) outputting 650 (node 5) @53|  |  |  |  |  |  |  |  ");else $display("Assert error:  pe_out[0+2*2](node 5) == %d @53, should be 650---------------------------------------------",pe_out[0+2*2]);
#10
$finish;

    end

endmodule
