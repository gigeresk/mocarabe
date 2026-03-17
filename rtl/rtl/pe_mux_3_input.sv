`include "mocarabe.h"
`include "benchmark.h"

module pe_mux_3_input #(
    parameter SCHED_LEN = 4,
    parameter X = 0,    // X address of this node
    parameter Y = 0     // Y address of this node
) (
    input  wire clk,        // clock
    input  wire rst,        // reset
    input  wire [`BENCHMARK_DATA_WIDTH-1:0] i0,
    input  wire [`BENCHMARK_DATA_WIDTH-1:0] i1,
    input  wire [`BENCHMARK_DATA_WIDTH-1:0] i2,
    output reg [`BENCHMARK_DATA_WIDTH-1:0] out0, // output to PE #1
    output reg [`BENCHMARK_DATA_WIDTH-1:0] out1  // output to PE #2
);

//changes for different channel num
reg [1:0] sel_memory0 [SCHED_LEN-1:0];
reg [1:0] sel_memory1 [SCHED_LEN-1:0];


initial begin //load sel memory
    $display("Loading sel memories at (%0d,%0d)", X, Y);
    //$readmemb({"mux3_sel_mem_x", $sformatf("%0d",X), "_y", $sformatf("%0d",Y), "0.dat"}, sel_memory0);
    //$readmemb({"mux3_sel_mem_x", $sformatf("%0d",X), "_y", $sformatf("%0d",Y), "1.dat"}, sel_memory1);
    $readmemb("mux3_sel_mem0.dat", sel_memory0);
    $readmemb("mux3_sel_mem1.dat", sel_memory1);
end

integer r;

reg [$clog2(SCHED_LEN)-1:0] now=0;

always @ (posedge clk)begin
    if (rst) begin
        now <= 0;
    end
    else begin
        if (now < (SCHED_LEN - 1))
            now <= now + 1;
        else
            now <= 0;
    end
end


always @* begin //first mux 
    case(sel_memory0[now])
        2'b00: begin
            out0 <= i0;     
        end
        2'b01: begin
            out0 <= i1;     
        end
        2'b10: begin
            out0 <= i2;     
        end
        default: begin
            out0 <= i0;
        end
    endcase
end


always @* begin //second mux
    case(sel_memory1[now])
        2'b00: begin
            out1 <= i0;     
        end
        2'b01: begin
            out1 <= i1;     
        end
        2'b10: begin
            out1 <= i2;     
        end
        default: begin
            out1 <= i0;
        end
    endcase
end


endmodule
