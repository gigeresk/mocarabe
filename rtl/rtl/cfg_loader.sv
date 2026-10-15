`include "mocarabe.h"

// Serial configuration front end for the soft bitstream.
//
// Protocol: hold cfg_en low for at least one clock (this resets the loader and
// the row token), then hold it high and send one CFG_W-bit word per clock.  A gap
// in cfg_en restarts programming from the first row.  Every
// WORDS words form a frame (FRAME_W bits, padded at the top to WORDS*CFG_W, most
// significant word first).  Each full frame is written into the row holding the
// one-hot configuration token, which then moves to the next row:
//   row 0: this module's global row (ii_last = II - 1)
//   then every PE's pe_cfg rows, in pe_idx = x + y*X_MAX order, slots 0..SCHED_LEN-1.
// Words after last row are ignored.
module cfg_loader #(
    parameter CFG_W = 1,
    parameter FRAME_W = 1,
    parameter II_W = 1,
    parameter STORAGE = "FLOP"  // TODO latch
) (
    input  wire clk,
    input  wire cfg_en,
    input  wire [CFG_W-1:0] cfg_data,
    output wire [FRAME_W-1:0] frame,
    output reg  frame_we,   // high for one cycle after each full frame
    output wire tok_out,    // token leaving the global row, into the first PE row
    output wire [II_W-1:0] ii_last
);
    localparam WORDS = (FRAME_W + CFG_W - 1) / CFG_W;
    localparam BUF_W = WORDS * CFG_W;
    localparam CNT_W = WORDS > 1 ? $clog2(WORDS) : 1;
    localparam [CNT_W-1:0] LAST_WORD = CNT_W'(WORDS - 1);

    reg [BUF_W-1:0] buffer;
    reg [CNT_W-1:0] words;
    reg tok;  // the global row holds the token until the first frame

    // shift each word in at the bottom
    generate
        if (WORDS == 1) begin : one_word_frames
            always @(posedge clk)
                if (cfg_en)
                    buffer <= cfg_data;
        end else begin : multi_word_frames
            always @(posedge clk)
                if (cfg_en)
                    buffer <= {buffer[BUF_W-CFG_W-1:0], cfg_data};
        end
    endgenerate

    always @(posedge clk) begin
        if (cfg_en) begin
            frame_we <= (words == LAST_WORD);
            words <= (words == LAST_WORD) ? {CNT_W{1'b0}} : words + 1'b1;
        end else begin
            frame_we <= 1'b0;
            words <= {CNT_W{1'b0}};
        end

        // the row holding the token is written by frame_we before the token moves on
        if (!cfg_en)
            tok <= 1'b1;
        else if (frame_we)
            tok <= 1'b0;
    end

    assign frame = buffer[FRAME_W-1:0];
    assign tok_out = tok;

    cfg_row #(.WIDTH(II_W), .STORAGE(STORAGE)) global_row (
        .clk(clk),
        .we(frame_we & tok),
        .d(frame[II_W-1:0]),
        .q(ii_last)
    );
endmodule
