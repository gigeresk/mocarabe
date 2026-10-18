/*
 * Copyright (c) 2026 Fred Tombs
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none
`include "mocarabe.h"
`include "benchmark.h"

// TinyTapeout wrapper for a Mocarabe array programmed through the soft bitstream.
//
// Pins:
//   ui_in[CFG_WIDTH-1:0]   cfg_data while configuring
//   ui_in[DATA_WIDTH-1:0]  the input bus while running: every IO PE reads it, each
//                          input in its own schedule slot
//   uio_in[0]              cfg_en
//   uo_out[DATA_WIDTH-1:0] io_out: in each output slot, one output of the kernel
//   uio_out[1]             io_out_valid: io_out holds an output slot's value
//   rst_n                  low resets the slot counters; hold it low while configuring
//
// Programming (see cfg_loader.sv): hold rst_n and cfg_en low for at least one clock,
// raise cfg_en and send one CFG_WIDTH-bit word of bitstream.hex per clock, drop
// cfg_en, then release rst_n.  Run cycle 0 is the first rising edge with rst_n high.
module tt_um_gigeresk_mocarabe (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);
    localparam N = `BENCHMARK_X_WIDTH * `BENCHMARK_Y_WIDTH;
    localparam D_W = `BENCHMARK_DATA_WIDTH;
    localparam CFG_W = `CFG_WIDTH;

    wire [D_W-1:0] io_out;
    wire io_out_valid;

    mocarabe array (
        .clk(clk),
        .rst(!rst_n),
        .cfg_en(uio_in[0]),
        .cfg_data(ui_in[CFG_W-1:0]),
        .io_data_in({N{ui_in[D_W-1:0]}}),
        .io_out(io_out),
        .io_out_valid(io_out_valid),
        .pe_o(),
        .pe_input0_o(),
        .pe_input1_o(),
        .done_pe(),
        .done_all()
    );

    assign uo_out  = io_out;
    assign uio_out = {6'b0, io_out_valid, 1'b0};
    assign uio_oe  = 8'b0000_0010;

    // List all unused inputs to prevent warnings
    wire _unused = &{ena, uio_in[7:1], 1'b0};

endmodule
