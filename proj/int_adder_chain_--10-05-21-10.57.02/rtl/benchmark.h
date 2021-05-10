// Application-specific macro parameters`define BENCHMARK_DATA_WIDTH 32
`define BENCHMARK_X_WIDTH 2
`define BENCHMARK_Y_WIDTH 3
`define BENCHMARK_SCHED_LEN 2
`define BENCHMARK_CHAN_WIDTH 2
`define BENCHMARK_DATA_WIDTH 32
`define FIFO_DEPTH 16
`define TORUS_SWITCH_PIPE_NUM  2
`define PE_PIPE_NUM 5//adder and u=multiplier configuration
    //must be modified for each configuration, with a bit for each pe. 0 is for an adder, and 1 is for a multiplier.the config bits are input from right to left, with the lsb being the
    //pe at top left, and msb being the pe at bottom right
    
//adder and u=multiplier configuration
//must be modified for each configuration, with a bit for each pe. 0 is for an adder, and 1 is for a multiplier.the config bits are input from right to left, with the lsb being the
//pe at top left, and msb being the pe at bottom right
`define PECONF 24'h020222
