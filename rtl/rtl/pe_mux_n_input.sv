`include "mocarabe.h"
`include "benchmark.h"

// Fanin from all NoC channels into the PE's two operand ports.
// Each port selects one channel per schedule slot (sel memories written by
// pe_memory_gen as pe_mux_x<X>_y<Y>_sel_mem<port>.dat).  Same timing as
// pe_mux_2_input.
module pe_mux_n_input #(
    parameter SCHED_LEN   = 4,
    parameter NUM_CHANNEL = 2,
    parameter X = 0,    // X address of this node
    parameter Y = 0     // Y address of this node
) (
    input  wire clk,
    input  wire rst,
    input  wire [`BENCHMARK_DATA_WIDTH-1:0] in [NUM_CHANNEL-1:0],
    output reg  [`BENCHMARK_DATA_WIDTH-1:0] out0, // output to PE port 0
    output reg  [`BENCHMARK_DATA_WIDTH-1:0] out1  // output to PE port 1
);

localparam SEL_W = NUM_CHANNEL > 1 ? $clog2(NUM_CHANNEL) : 1;
localparam NOW_BITWIDTH = SCHED_LEN == 1 ? 1 : $clog2(SCHED_LEN);

reg [SEL_W-1:0] sel_memory0 [SCHED_LEN-1:0];
reg [SEL_W-1:0] sel_memory1 [SCHED_LEN-1:0];

initial begin
    $readmemb($sformatf("%spe_mux_x%0d_y%0d_sel_mem0.dat", `MOCARABE_DAT_DIR, X, Y), sel_memory0);
    $readmemb($sformatf("%spe_mux_x%0d_y%0d_sel_mem1.dat", `MOCARABE_DAT_DIR, X, Y), sel_memory1);
end

reg [NOW_BITWIDTH:0] now = 0;

always @(posedge clk) begin
    if (rst)
        now <= 0;
    else if (now < (SCHED_LEN - 1))
        now <= now + 1;
    else
        now <= 0;
end

always @* begin
    out0 = (sel_memory0[now] < NUM_CHANNEL) ? in[sel_memory0[now]] : in[0];
    out1 = (sel_memory1[now] < NUM_CHANNEL) ? in[sel_memory1[now]] : in[0];
end

endmodule
