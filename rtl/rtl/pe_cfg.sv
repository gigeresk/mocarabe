`include "mocarabe.h"

// One PE's soft-bitstream configuration: a row per schedule slot, each written
// while it holds the configuration token (see cfg_loader.sv).
//
// Row t holds slot t's frame (FRAME_W bits, LSB first):
//   per channel c:  [6c+1:6c] north select, [6c+3:6c+2] east, [6c+5:6c+4] to-PE
//   then op1 SRL address (ADDR_W), op2 SRL address (ADDR_W),
//   then PE fan-in mux select for port 0 (SEL_W) and port 1 (SEL_W).
module pe_cfg #(
    parameter SCHED_LEN = 4,
    parameter FRAME_W = 1,
    parameter STORAGE = "FLOP"
) (
    input  wire clk,
    input  wire cfg_en,
    input  wire frame_we,
    input  wire [FRAME_W-1:0] frame,
    input  wire tok_in,     // token from the previous row
    output wire tok_out,    // token to the next PE's first row
    output wire [SCHED_LEN*FRAME_W-1:0] rows  // slot t at [t*FRAME_W +: FRAME_W]
);
    reg [SCHED_LEN-1:0] tok;

    // the token moves up one row per frame
    generate
        if (SCHED_LEN == 1) begin : one_slot
            always @(posedge clk)
                if (!cfg_en)
                    tok <= 1'b0;
                else if (frame_we)
                    tok <= tok_in;
        end else begin : slots
            always @(posedge clk)
                if (!cfg_en)
                    tok <= {SCHED_LEN{1'b0}};
                else if (frame_we)
                    tok <= {tok[SCHED_LEN-2:0], tok_in};
        end
    endgenerate

    assign tok_out = tok[SCHED_LEN-1];

    genvar t;
    generate
        for (t = 0; t < SCHED_LEN; t = t + 1) begin : slot
            cfg_row #(.WIDTH(FRAME_W), .STORAGE(STORAGE)) row (
                .clk(clk),
                .we(frame_we & tok[t]),
                .d(frame),
                .q(rows[t*FRAME_W +: FRAME_W])
            );
        end
    endgenerate
endmodule
