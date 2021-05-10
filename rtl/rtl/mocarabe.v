`include "mocarabe.h"
`include "benchmark.h"

module mocarabe #(
    parameter SCHED_LEN = `BENCHMARK_SCHED_LEN, 
    parameter X_MAX     = `BENCHMARK_X_WIDTH,
    parameter Y_MAX     =  `BENCHMARK_Y_WIDTH,
    parameter PIPENUM   =   1,
    parameter NUM_CHANNEL = `BENCHMARK_CHAN_WIDTH,
    parameter PECONFIG = `PECONF,
    // parameter `XY PECONFIG = `PECONF,
    parameter PE_PIPE = 1    
) (
    input  wire clk,
    input  wire rst,
    output wire `D_WIDTH pe_o0,
    output wire done_pe,
    output wire done_all
);
    
    wire [NUM_CHANNEL*X_MAX*Y_MAX-1:0]  done;
    wire `XY    done_a_pe;
    wire `D_WIDTH horiz [X_MAX*Y_MAX-1:0][NUM_CHANNEL-1:0];     // eastbound channels
    wire `D_WIDTH vert [X_MAX*Y_MAX-1:0][NUM_CHANNEL-1:0];      // northbound/output channels
    wire `D_WIDTH i_from_pe `XY; // from a pe to a noc node
    wire `D_WIDTH o_to_pe [X_MAX*Y_MAX-1:0][NUM_CHANNEL-1:0]; // from noc to pe
    wire `D_WIDTH mux_to_pe [NUM_CHANNEL-1:0][X_MAX*Y_MAX-1:0];//router to pe mux output

    reg [$clog2(SCHED_LEN)-1:0] now=0; //bitwidth of schedule

    assign pe_o0 = i_from_pe[0];

    always @(posedge clk) begin
        if(rst) begin
            now <= 0;
        end else begin
            if (now > SCHED_LEN - 1)begin
                $finish();
            end
            now <= now + 1;
        end
    end

    genvar x, y, c;
    generate
    for (y = 0; y < Y_MAX; y = y + 1) begin : ys 
        for (x = 0; x < X_MAX; x = x + 1) begin : xs
            if(NUM_CHANNEL > 1)begin

                pe_2_input #(
                    .SCHED_LEN(SCHED_LEN),
                    .X_MAX(X_MAX),
                    .Y_MAX(Y_MAX),
                    .X(x),
                    .Y(y),
                    .OP(PECONFIG[(4*((x) + (y)*X_MAX)+3):4*((x) + (y)*X_MAX)]),
                    .PIPE(PE_PIPE)
                    )
                    pe_inst
                    (
                        .clk(clk),
                        .done_a_pe(done_a_pe[(x) + (y)*X_MAX]),
                        .i_operand0(mux_to_pe [0][(x) + (y)*X_MAX]),
                        .i_operand1(mux_to_pe [1][(x) + (y)*X_MAX]),
                        .result(i_from_pe[(x) + (y)*X_MAX])
                    );
                for (c = 0; c < NUM_CHANNEL; c = c + 1) begin : cs
                    torus_switch #(
                        .SCHED_LEN(SCHED_LEN),
                        .X_MAX(X_MAX),
                        .Y_MAX(Y_MAX),
                        .X(x),
                        .Y(y), 
                        .PIPENUM(PIPENUM),
                        .C(c)
                    )
                    torus_switch_inst
                    (
                        .clk(clk),
                        .rst(rst),
                        .s_in(vert[ ((x) +((y+Y_MAX-1)%Y_MAX)*X_MAX)][c]),
                        .w_in(horiz[(((x+X_MAX-1)%X_MAX)+(y)*X_MAX)][c]),
                        .i_from_pe(i_from_pe[(x) + (y)*X_MAX]),
                        .o_to_pe(o_to_pe[(x) + (y)*X_MAX][c]),
                        .done(done[NUM_CHANNEL*((x) + (y)*X_MAX) + c]),//a bit for each channel, modified for multichannel
                        .n_out(vert[(x) + (y)*X_MAX][c]),
                        .e_out(horiz[(x) + (y)*X_MAX][c])
                    );
                end
                //fanin for 3 channels to 2 PE inputs
                if (NUM_CHANNEL == 3)begin
                    pe_mux_3_input #(
                        .SCHED_LEN(SCHED_LEN),
                        .X(x),
                        .Y(y)
                    ) 
                    mux_inst
                    (
                        .clk(clk),
                        .rst(rst),
                        .i0(o_to_pe[(x) + (y)*X_MAX][0]),
                        .i1(o_to_pe[(x) + (y)*X_MAX][1]),
                        .i2(o_to_pe[(x) + (y)*X_MAX][2]),
                        .out0(mux_to_pe[0][(x) + (y)*X_MAX]),
                        .out1(mux_to_pe[1][(x) + (y)*X_MAX])
                    );
                end
                //fanin for 2 channels to 2 PE inputs
                else begin
                    pe_mux_2_input #(
                        .SCHED_LEN(SCHED_LEN),
                        .X(x),
                        .Y(y)
                    ) 
                    mux_inst
                    (
                        .clk(clk),
                        .rst(rst),
                        .i0(o_to_pe[(x) + (y)*X_MAX][0]),
                        .i1(o_to_pe[(x) + (y)*X_MAX][1]),
                        .out0(mux_to_pe[0][(x) + (y)*X_MAX]),
                        .out1(mux_to_pe[1][(x) + (y)*X_MAX])
                    );    
                end

            end
            //C = 1, single input PE
            else begin
                pe_1_input #(
                    .SCHED_LEN(SCHED_LEN),
                    .X_MAX(X_MAX),
                    .Y_MAX(Y_MAX),
                    .X(x),
                    .Y(y),
                    .OP(PECONFIG[(x) + (y)*X_MAX]),
                    .PIPE(PE_PIPE)
                    )
                    pe_inst
                    (
                        .clk(clk),
                        .done_a_pe(done_a_pe[(x) + (y)*X_MAX]),
                        .i_operand(o_to_pe[(x) + (y)*X_MAX][0]),
                        .result(i_from_pe[(x) + (y)*X_MAX])
                    );
                    
                    torus_switch #(
                        .SCHED_LEN(SCHED_LEN),
                        .X_MAX(X_MAX),
                        .Y_MAX(Y_MAX),
                        .X(x),
                        .Y(y), 
                        .PIPENUM(PIPENUM)
                    )
                    torus_switch_inst
                    (
                        .clk(clk),
                        .rst(rst),
                        .s_in(vert[ ((x) +((y+Y_MAX-1)%Y_MAX)*X_MAX)][0]),
                        .w_in(horiz[(((x+X_MAX-1)%X_MAX)+(y)*X_MAX)][0]),
                        .i_from_pe(i_from_pe[(x) + (y)*X_MAX]),
                        .o_to_pe(o_to_pe[(x) + (y)*X_MAX][0]),
                        .done(done[NUM_CHANNEL*((x) + (y)*X_MAX)]),
                        .n_out(vert[(x) + (y)*X_MAX][0]),
                        .e_out(horiz[(x) + (y)*X_MAX][0])
                    );
            end
        end
    end
    endgenerate

    assign done_all = &done;
    assign done_pe = &done_a_pe;
`ifdef DEBUG
    initial begin
            $dumpfile("mocarabe.vcd");
            $dumpvars(0,mocarabe);
        end
`endif

endmodule

