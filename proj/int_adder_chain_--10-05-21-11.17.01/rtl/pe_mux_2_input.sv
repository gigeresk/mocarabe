`include "mocarabe.h"
`include "benchmark.h"

module pe_mux_2_input #(
    parameter SCHED_LEN = 4,
    parameter X	= 0,	// X address of this node
    parameter Y	= 0		// Y address of this node
) (
    input  wire clk,		// clock
    input  wire rst,		// reset
    input  wire [`BENCHMARK_DATA_WIDTH-1:0] i0,
    input  wire [`BENCHMARK_DATA_WIDTH-1:0] i1,
    output reg [`BENCHMARK_DATA_WIDTH-1:0] out0, // output to PE #1
    output reg [`BENCHMARK_DATA_WIDTH-1:0] out1  // output to PE #2
);

//change for different channel num
reg sel_memory0 [SCHED_LEN-1:0];
reg sel_memory1 [SCHED_LEN-1:0];
localparam NOW_BITWIDTH = SCHED_LEN==1? 1: $clog2(SCHED_LEN);

initial begin //load sel memory
    $display("Loading sel memories at (%0d,%0d)", X, Y);
    //TODO: uncomment this when testing final stuff in the end-to-end flow.
    //$readmemb({"mux2_sel_mem_x", $sformatf("%0d",X), "_y", $sformatf("%0d",Y), "0.dat"}, sel_memory0);
    //$readmemb({"mux2_sel_mem_x", $sformatf("%0d",X), "_y", $sformatf("%0d",Y), "1.dat"}, sel_memory1);
    $readmemb($sformatf("mux2_x%0d_y%0d_sel_mem0.dat", X, Y), sel_memory0);
    $readmemb($sformatf("mux2_x%0d_y%0d_sel_mem1.dat", X, Y), sel_memory1);
end

integer r;

reg [NOW_BITWIDTH:0] now=0;

always @ (posedge clk)begin
    if (rst) begin
        now <= 0;
    end
    else begin
        $display("(%0d,%0d): i0: %0d, i1: %0d,out0: %0d, out1: %0d\n",X,Y,i0,i1,out0,out1 );
        if (now < (SCHED_LEN - 1))
            now <= now + 1;
        else
            now <= 0;
    end
end

always @* begin //first mux
    case(sel_memory0[now])
        2'b0: begin
            out0 <= i0;
        end
        2'b1: begin
            out0 <= i1;
        end
        default: begin
            out0 <= i0;
        end
    endcase
end


always @* begin //second mux
    case(sel_memory1[now])
        2'b0: begin
            out1 <= i0;
        end
        2'b1: begin
            out1 <= i1;
        end
        default: begin
            out1 <= i1;
        end
    endcase
end


endmodule
