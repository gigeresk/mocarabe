'''
Need to generate mocarabe.v for simulation, can't use genvar effectively.
This shouldn't be used for synthesis because there are too many top-level output ports (one for each PE, pe_out)
Keep up to date with master RTL.

Diff:
+ output port from every PE to top-level Mocarabe

+/- Replaced generate loop (and the genvars) with unique instance, each with
  unique names (and replacing x,y,c with actual values)
Don't leave these for synthesis.  This is an easier way to verify correctness
'''
def mocarabe_tb_gen( rtl_dir, Nx, Ny, C ):


    top = \
    '''
`include "mocarabe.h"
`include "benchmark.h"

//3 channel - 2 input pe array - TODO - change with golden RTL covering all configs

module mocarabe #(
    parameter SCHED_LEN = `BENCHMARK_SCHED_LEN,
    parameter X_MAX     = `BENCHMARK_X_WIDTH,
    parameter Y_MAX     =  `BENCHMARK_Y_WIDTH,
    parameter PIPENUM   =   1,
    parameter num_channel = `BENCHMARK_CHAN_WIDTH,
    parameter `XY PECONFIG = `PECONF
) (
    input  wire clk,
    input  wire rst,
    input  wire ce,


    output wire `D_WIDTH pe_out `XY,
    output wire done_pe,
    output wire done_all
);

    wire [num_channel*X_MAX*Y_MAX-1:0]  done;
    wire `XY    done_a_pe;
    wire `D_WIDTH horiz [X_MAX*Y_MAX-1:0][num_channel-1:0];     // eastbound channels
    wire `D_WIDTH vert [X_MAX*Y_MAX-1:0][num_channel-1:0];      // northbound/output channels
    wire `D_WIDTH i_from_pe `XY; // from a pe to a noc node
    wire `D_WIDTH o_to_pe [X_MAX*Y_MAX-1:0][num_channel-1:0]; // from noc to pe
    wire `D_WIDTH mux_to_pe0 `XY;//router to pe mux output
    wire `D_WIDTH mux_to_pe1 `XY;//router to pe mux output
    integer cycle = 0;

    reg [$clog2(SCHED_LEN)-1:0] now=0; //bitwidth of schedule

    //assign pe_o0 = i_from_pe[0];

    always @(posedge clk) begin
        cycle = cycle + 1;

        if(rst) begin
            now <= 0;
        end else begin
            now <= now + 1;
        end
    end

    genvar x,y; // In this simulation, genvars only used for this assign
    for (x=0; x < X_MAX; x = x + 1) begin
        for (y=0; y < Y_MAX; y = y + 1) begin
            assign pe_out[x + y*X_MAX] = i_from_pe[x + y*X_MAX];
        end
    end

'''
    print( top )

    instances_string = ""
    pe_instances_string = ""

    for y in range( Ny ):
        for x in range( Nx ):

            instances_string = instances_string + \
f'''
pe #(
    .SCHED_LEN(SCHED_LEN),
    .X_MAX(X_MAX),
    .Y_MAX(Y_MAX),
    .X({x}),
    .Y({y}),
    .OP(PECONFIG[({x}) + ({y})*X_MAX])
    )
    pe_inst_x{x}_y{y}
    (
        .clk(clk),
        .done_a_pe(done_a_pe[({x}) + ({y})*X_MAX]),
        .i_operand0(mux_to_pe0[({x}) + ({y})*X_MAX]),
        .i_operand1(mux_to_pe1[({x}) + ({y})*X_MAX]),
        .result(i_from_pe[({x}) + ({y})*X_MAX])
    );

//this is currently fixed for c=3 and i=2
pe_mux #(
    .SCHED_LEN(SCHED_LEN),
    .X({x}),
    .Y({y})
)
mux_inst_x{x}_y{y}
(
    .clk(clk),
    .rst(rst),
    .i0(o_to_pe[({x}) + ({y})*X_MAX][0]),
    .i1(o_to_pe[({x}) + ({y})*X_MAX][1]),
    .i2(o_to_pe[({x}) + ({y})*X_MAX][2]),
    .out0(mux_to_pe0[({x}) + ({y})*X_MAX]),
    .out1(mux_to_pe1[({x}) + ({y})*X_MAX])
);
'''
    for y in range( Ny ):
            for x in range( Nx ):
                for c in range( C ):
                    instances_string = instances_string +  \
f'''
torus_switch #(
    .SCHED_LEN(SCHED_LEN),
    .X_MAX(X_MAX),
    .Y_MAX(Y_MAX),
    .X({x}),
    .Y({y}),
    .PIPENUM(PIPENUM)
    )
    torus_switch_inst_x{x}_y{y}_c{c}
    (
        .clk(clk),
        .rst(rst),
        .s_in(vert[ (({x}) +(({y}+Y_MAX-1)%Y_MAX)*X_MAX)][{c}]),
        .w_in(horiz[((({x}+X_MAX-1)%X_MAX)+({y})*X_MAX)][{c}]),
        .i_from_pe(i_from_pe[({x}) + ({y})*X_MAX]),// all four xy
        .o_to_pe(o_to_pe[({x}) + ({y})*X_MAX][{c}]),
        .done(done[num_channel*(({x}) + ({y})*X_MAX) + {c}]),//a bit for each channel, modified for multichannel
        .n_out(vert[({x}) + ({y})*X_MAX][{c}]),
        .e_out(horiz[({x}) + ({y})*X_MAX][{c}])
    );
    '''
    print( instances_string )




    tail = \
'''
    assign done_all = &done;
    assign done_pe = &done_a_pe;
`ifdef DEBUG
    initial begin
            $dumpfile("mocarabe.vcd");
            $dumpvars(0,mocarabe);
        end
`endif

endmodule
'''

    f = open( f"{rtl_dir}/mocarabe_tb.v" , "w+" )
    f.write( top + instances_string + tail )
    return top + instances_string + tail