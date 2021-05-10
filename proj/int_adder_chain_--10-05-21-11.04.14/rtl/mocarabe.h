// Application-independent macros

`timescale 1ns/1ps

`define XY [X_MAX*Y_MAX-1:0]
`define SCHED [SCHED_LEN-1:0]
`define X       [X_W-1:0]
`define Y       [Y_W-1:0]

// `define PECONF  19'b1111111111111111111


`define D_WIDTH [`BENCHMARK_DATA_WIDTH-1:0]
