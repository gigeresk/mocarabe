`include "mocarabe.h"
`include "benchmark.h"

module mocarabe #(
    // soft bitstream: memories hold II_MAX slots and the programmed II picks how many run
    parameter SCHED_LEN = `BITSTREAM_SOFT ? `BENCHMARK_II_MAX : `BENCHMARK_SCHED_LEN,
    parameter X_MAX     = `BENCHMARK_X_WIDTH,
    parameter Y_MAX     =  `BENCHMARK_Y_WIDTH,
    parameter PIPENUM   =   1,
    parameter NUM_CHANNEL = `BENCHMARK_CHAN_WIDTH,
    parameter [4*X_MAX*Y_MAX-1:0] PECONFIG = `PECONF,
    // parameter `XY PECONFIG = `PECONF,
    parameter PE_PIPE = `PE_PIPE_NUM,
    parameter D_W = `BENCHMARK_DATA_WIDTH,
    parameter CFG_W = `CFG_WIDTH,
    parameter CFG_STORAGE = "FLOP"
) (
    input  wire clk,
    input  wire rst,
    // soft bitstream programming port (unused with the hard bitstream), see cfg_loader.sv
    input  wire cfg_en,
    input  wire [CFG_W-1:0] cfg_data,
    input  wire [D_W-1:0] io_data_in [X_MAX*Y_MAX-1:0],
    output wire [D_W-1:0] pe_o [X_MAX*Y_MAX-1:0],
    output wire [D_W-1:0] pe_input0_o [X_MAX*Y_MAX-1:0],
    output wire [D_W-1:0] pe_input1_o [X_MAX*Y_MAX-1:0],
    output wire done_pe,
    output wire done_all
);

    wire [NUM_CHANNEL*X_MAX*Y_MAX-1:0]  done;
    wire `XY    done_a_pe;
    wire [D_W-1:0] horiz [X_MAX*Y_MAX-1:0][NUM_CHANNEL-1:0];     // eastbound channels
    wire [D_W-1:0] vert [X_MAX*Y_MAX-1:0][NUM_CHANNEL-1:0];      // northbound/output channels
    wire [D_W-1:0] i_from_pe `XY; // from a pe to a noc node
    wire [D_W-1:0] o_to_pe [X_MAX*Y_MAX-1:0][NUM_CHANNEL-1:0]; // from noc to pe
    wire [D_W-1:0] mux_to_pe [NUM_CHANNEL-1:0][X_MAX*Y_MAX-1:0];//router to pe mux output

    reg [$clog2(SCHED_LEN)-1:0] now=0; //bitwidth of schedule

    // Soft bitstream frame: one PE's configuration for one schedule slot (see pe_cfg.sv)
    localparam NOW_W = SCHED_LEN == 1 ? 1 : $clog2(SCHED_LEN);
    localparam ADDR_W = $clog2(`FIFO_DEPTH);
    localparam SEL_W = NUM_CHANNEL > 1 ? $clog2(NUM_CHANNEL) : 1;
    localparam FRAME_W = 6*NUM_CHANNEL + 2*ADDR_W + 2*SEL_W;

    wire [NOW_W-1:0] sched_last;  // II - 1: where every slot counter wraps
    wire [FRAME_W-1:0] cfg_frame;
    wire cfg_frame_we;
    wire cfg_tok [X_MAX*Y_MAX:0];  // configuration token chain, global row then PEs

    generate
        if (`BITSTREAM_SOFT) begin : soft_bitstream
            cfg_loader #(
                .CFG_W(CFG_W),
                .FRAME_W(FRAME_W),
                .II_W(NOW_W),
                .STORAGE(CFG_STORAGE)
            ) loader (
                .clk(clk),
                .cfg_en(cfg_en),
                .cfg_data(cfg_data),
                .frame(cfg_frame),
                .frame_we(cfg_frame_we),
                .tok_out(cfg_tok[0]),
                .ii_last(sched_last)
            );
        end else begin : hard_bitstream
            assign sched_last = SCHED_LEN - 1;
        end
    endgenerate

    //assign pe_o0 = i_from_pe[0];

    always @(posedge clk) begin
        if(rst) begin
            now <= 0;
        end else begin
            now <= now + 1;
        end
    end
    //for simulation only
    //to have an output port for each pe output
    genvar x_o, y_o;
    generate
        for (y_o = 0; y_o < Y_MAX; y_o = y_o + 1) begin : x_out
            for (x_o = 0; x_o < X_MAX; x_o = x_o + 1) begin : y_out
                assign pe_o[(x_o) + (y_o)*X_MAX] = i_from_pe[(x_o) + (y_o)*X_MAX];
                assign pe_input0_o[(x_o) + (y_o)*X_MAX] = mux_to_pe[0][(x_o) + (y_o)*X_MAX];
                assign pe_input1_o[(x_o) + (y_o)*X_MAX] = mux_to_pe[1][(x_o) + (y_o)*X_MAX];
            end
        end
    endgenerate



    genvar x, y, c, t;
    generate
    for (y = 0; y < Y_MAX; y = y + 1) begin : ys
        for (x = 0; x < X_MAX; x = x + 1) begin : xs
            if(NUM_CHANNEL > 1)begin
                // this PE's configuration: slot t's frame at cfg_rows[t*FRAME_W +: FRAME_W]
                wire [SCHED_LEN*FRAME_W-1:0] cfg_rows;
                wire [SCHED_LEN*6-1:0] switch_cfg [NUM_CHANNEL-1:0];
                wire [SCHED_LEN*2*ADDR_W-1:0] pe_cfg_addr;
                wire [SCHED_LEN*2*SEL_W-1:0] mux_cfg;
                if (`BITSTREAM_SOFT) begin : soft_bitstream
                    pe_cfg #(
                        .SCHED_LEN(SCHED_LEN),
                        .FRAME_W(FRAME_W),
                        .STORAGE(CFG_STORAGE)
                    ) cfg_inst (
                        .clk(clk),
                        .cfg_en(cfg_en),
                        .frame_we(cfg_frame_we),
                        .frame(cfg_frame),
                        .tok_in(cfg_tok[(x) + (y)*X_MAX]),
                        .tok_out(cfg_tok[(x) + (y)*X_MAX + 1]),
                        .rows(cfg_rows)
                    );
                end else begin : hard_bitstream
                    assign cfg_rows = 0;
                end
                for (t = 0; t < SCHED_LEN; t = t + 1) begin : cfg_slots
                    for (c = 0; c < NUM_CHANNEL; c = c + 1) begin : cfg_channels
                        assign switch_cfg[c][t*6 +: 6] = cfg_rows[t*FRAME_W + 6*c +: 6];
                    end
                    assign pe_cfg_addr[t*2*ADDR_W +: 2*ADDR_W] =
                        cfg_rows[t*FRAME_W + 6*NUM_CHANNEL +: 2*ADDR_W];
                    assign mux_cfg[t*2*SEL_W +: 2*SEL_W] =
                        cfg_rows[t*FRAME_W + 6*NUM_CHANNEL + 2*ADDR_W +: 2*SEL_W];
                end

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
                        .rst(rst),
                        .done_a_pe(done_a_pe[(x) + (y)*X_MAX]),
                        .i_operand0(mux_to_pe [0][(x) + (y)*X_MAX]),
                        .i_operand1(mux_to_pe [1][(x) + (y)*X_MAX]),
                        .io_input(io_data_in[(x) + (y)*X_MAX]),
                        .result(i_from_pe[(x) + (y)*X_MAX]),
                        .cfg(pe_cfg_addr),
                        .sched_last(sched_last)
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
                        .e_out(horiz[(x) + (y)*X_MAX][c]),
                        .cfg(switch_cfg[c]),
                        .sched_last(sched_last)
                    );
                end
                //fanin from every channel to the 2 PE inputs
                wire [D_W-1:0] mux_in [NUM_CHANNEL-1:0];
                for (c = 0; c < NUM_CHANNEL; c = c + 1) begin : mux_ins
                    assign mux_in[c] = o_to_pe[(x) + (y)*X_MAX][c];
                end
                pe_mux_n_input #(
                    .SCHED_LEN(SCHED_LEN),
                    .NUM_CHANNEL(NUM_CHANNEL),
                    .X(x),
                    .Y(y)
                )
                mux_inst
                (
                    .clk(clk),
                    .rst(rst),
                    .in(mux_in),
                    .out0(mux_to_pe[0][(x) + (y)*X_MAX]),
                    .out1(mux_to_pe[1][(x) + (y)*X_MAX]),
                    .cfg(mux_cfg),
                    .sched_last(sched_last)
                );

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
                        .e_out(horiz[(x) + (y)*X_MAX][0]),
                        .cfg({SCHED_LEN*6{1'b0}}),  // the soft bitstream needs C > 1
                        .sched_last(sched_last)
                    );
            end
        end
    end
    endgenerate

    assign done_all = &done;
    assign done_pe = &done_a_pe;
// DEBUG leaks in from torus_switch.sv, so also exclude the dump from synthesis
`ifdef DEBUG
`ifndef SYNTHESIS
    initial begin
            $dumpfile("mocarabe.vcd");
            $dumpvars(0,mocarabe);
        end
`endif
`endif

endmodule

