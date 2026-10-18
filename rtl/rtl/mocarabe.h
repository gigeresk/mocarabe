// Application-independent macros

`timescale 1ns/1ps

`define XY [X_MAX*Y_MAX-1:0]
`define SCHED [SCHED_LEN-1:0]
`define X       [X_W-1:0]
`define Y       [Y_W-1:0]

// `define PECONF  19'b1111111111111111111


`define D_WIDTH [`BENCHMARK_DATA_WIDTH-1:0]

// Directory prefix (with trailing slash) for $readmem schedule files.
// Empty by default, so files are read relative to the working directory (simulation).
// Synthesis flows that run elsewhere pass an absolute path, e.g. -DMOCARABE_DAT_DIR="/abs/rtl/".
`ifndef MOCARABE_DAT_DIR
`define MOCARABE_DAT_DIR ""
`endif

// Per-cycle $display chatter from the PEs and switches: simulation only, and off
// with -DMOCARABE_QUIET
`ifndef SYNTHESIS
`ifndef MOCARABE_QUIET
`define MOCARABE_VERBOSE
`endif
`endif
