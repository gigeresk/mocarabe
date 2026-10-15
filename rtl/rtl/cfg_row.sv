`include "mocarabe.h"

// One row of configuration storage, written from the frame buffer while the row
// holds the configuration token.
//
// STORAGE = "FLOP" is implemented.  "LATCH" is reserved: each cell would open only
// while its row is written (we comes straight from a token flop, so it is
// glitch-free) and copy from the steady frame-buffer flops, so the timing
// constraints reduce to a setup check around the enable closing plus static
// configuration in run mode.
module cfg_row #(
    parameter WIDTH = 1,
    parameter STORAGE = "FLOP"
) (
    input  wire clk,
    input  wire we,
    input  wire [WIDTH-1:0] d,
    output reg  [WIDTH-1:0] q
);
    generate
        if (STORAGE == "FLOP") begin : flop
            always @(posedge clk)
                if (we)
                    q <= d;
        end else begin : unsupported
            initial $fatal(1, "cfg_row: STORAGE \"%s\" is not implemented", STORAGE);
        end
    endgenerate
endmodule
