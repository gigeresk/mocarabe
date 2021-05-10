`include "mocarabe.h"
`include "benchmark.h"

module torus_switch #(
    parameter SCHED_LEN = 4,
    parameter X_MAX = 4,
    parameter Y_MAX = 4,
    parameter X = 0,    // X address of this node
    parameter Y = 0,        // Y address of this node
    parameter PIPENUM = `TORUS_SWITCH_PIPE_NUM,
    parameter C = 0
) (
    input  wire clk,        // clock
    input  wire rst,        // reset
    input  wire `D_WIDTH s_in,  // input data from south
    input  wire `D_WIDTH w_in,  // input data from east
    input  wire `D_WIDTH i_from_pe,     // input data from PE
    output wire `D_WIDTH o_to_pe, // output from this noc node to local PE
    output wire `D_WIDTH n_out, // northbound output data
    output wire `D_WIDTH e_out, // eastbound output data
    output reg done // no data being processed
);

    reg  `D_WIDTH s;            // south input data register
    reg  `D_WIDTH w;            // west input data register
    reg  `D_WIDTH w_r;          // only for done signal
    reg  `D_WIDTH s_r;          // only for done signal

    localparam NOW_BITWIDTH = SCHED_LEN==1? 1: $clog2(SCHED_LEN);
    // Northbound mux select memory
    reg [1:0] n_bound_sel_memory[SCHED_LEN-1:0];
    // Eastbound mux select memory
    reg [1:0] e_bound_sel_memory[SCHED_LEN-1:0];
    // Into-PE mux select memory
    reg [1:0] pe_bound_sel_memory[SCHED_LEN-1:0];

    reg  `D_WIDTH e_out_r;
    (* dont_touch = "true" *) reg  `D_WIDTH e_out_pipe [PIPENUM-1:0];
    reg  `D_WIDTH n_out_r;
    (* dont_touch = "true" *) reg  `D_WIDTH n_out_pipe [PIPENUM-1:0];
    reg  `D_WIDTH o_to_pe_r;
    (* dont_touch = "true" *) reg  `D_WIDTH o_to_pe_pipe [PIPENUM-1:0];
    reg `D_WIDTH e_out_c, n_out_c, o_to_pe_c;
    reg [NOW_BITWIDTH-1:0] now=0; //bitwidth of schedule

    reg `D_WIDTH s_in_reg;
    reg `D_WIDTH w_in_reg;
    reg `D_WIDTH i_from_pe_reg;

    initial begin
        $readmemb($sformatf("noc_memory_n_x%0d_y%0d_c%0d.dat", X, Y, C), n_bound_sel_memory);
		$readmemb($sformatf("noc_memory_e_x%0d_y%0d_c%0d.dat", X, Y, C), e_bound_sel_memory);
		$readmemb($sformatf("noc_memory_pe_x%0d_y%0d_c%0d.dat", X, Y, C), pe_bound_sel_memory);
       done = 0;
       e_out_r = 0;
       n_out_r = 0;
       o_to_pe_r = 0;
       s = 0;
       w = 0;
       w_r = 0;
       s_in_reg = 0;
       w_in_reg = 0;
       i_from_pe_reg = 0;
    end

    // Register inputs
    always @(posedge clk) begin
        if(rst) begin
            s_in_reg <= 0;
            w_in_reg <= 0;
            i_from_pe_reg <= 0;
        end
        else begin
            s_in_reg <= s_in;
            w_in_reg <= w_in;
            i_from_pe_reg <= i_from_pe;
        end
    end

    // Register outputs
    always @(posedge clk) begin
        if(rst) begin
            e_out_r <= 0;
            n_out_r <= 0;
            now <= 0;
        end else begin
            n_out_r <= n_out_c;
            e_out_r <= e_out_c;
            o_to_pe_r <= o_to_pe_c;
            now <= now + 1;

            if( now == SCHED_LEN - 1 )
                now <= 0;
            else
                now <= now + 1;
            `define DEBUG 1
            `ifdef DEBUG
                $display("(%0d,%0d), cycle ",X,Y,now);
                $display("inputs %0d south, %0d west, %0d from PE ", s_in, w_in, i_from_pe);
                $display("sending %0d north, %0d east, %0d to PE ", n_out_r, e_out_r, o_to_pe);
            `endif

        end

    end

    // Switch logic (combinational)

    always @* begin
    // Northbound Mux
    // Inputs: West channel, South channel, local PE (assuming IO_O = 1)
    // Sel: Memory with size # cycles in schedule
    // Output: North channel

        case(n_bound_sel_memory[now][1:0])
            2'b00: begin
                n_out_c = s_in_reg;     // Send from S
            end
            2'b01: begin
                n_out_c = w_in_reg;     // Send from W
            end
            2'b10: begin
                n_out_c = i_from_pe_reg;    // Send from PE
            end
            2'b11: begin
                n_out_c = {`BENCHMARK_DATA_WIDTH{1'b0}};;
            end
        endcase

    // Eastbound Mux
    // Inputs: West channel, South channel, local PE (assuming IO_O = 1)
    // Sel: Memory with size # cycles in schedule
    // Output: East channel
        case(e_bound_sel_memory[now][1:0])
            2'b00: begin
                e_out_c = s_in_reg;
            end
            2'b01: begin
                e_out_c = w_in_reg;
            end
            2'b10: begin
                e_out_c = i_from_pe_reg;
            end
            // TODO set to 14 for now, but needs to be improved
            2'b11: begin
                e_out_c = {`BENCHMARK_DATA_WIDTH{1'b0}};
            end
        endcase

    // Into-PE Mux
    // Inputs: West channel, South channel (assuming IO_O = 1)
    // Sel: Memory with size # cycles in schedule
    // Output: East channel
        case(pe_bound_sel_memory[now][1:0])
            2'b00: o_to_pe_c = s_in_reg;    // s to pe
            2'b01: o_to_pe_c = w_in_reg;    // w to pe
            2'b10: o_to_pe_c = i_from_pe_reg;   // nothing to PE (should disable the CE to srl16)
            2'b11: o_to_pe_c = {`BENCHMARK_DATA_WIDTH{1'b0}};
        endcase
    end
    //pipelining outputs
    genvar i;
    generate
        for (i=0;i<PIPENUM;i=i+1) begin
            if(i == 0)begin
                always @(posedge clk) begin
                    if(rst)begin
                        n_out_pipe[0]<=0;
                        e_out_pipe[0]<=0;
                        o_to_pe_pipe[0] <= 0;
                    end
                    else begin
                        n_out_pipe[0]<=n_out_r;
                        e_out_pipe[0]<=e_out_r;
                        o_to_pe_pipe[0]<=o_to_pe_r;
                    end
                end
            end
            else begin
                always @(posedge clk) begin
                    if(rst)begin
                        n_out_pipe[i]   <=  0;
                        e_out_pipe[i]   <=  0;
                    end
                    else begin
                        n_out_pipe[i]   <=  n_out_pipe[i-1];
                        e_out_pipe[i]   <=  e_out_pipe[i-1];
                        o_to_pe_pipe[i] <= o_to_pe_pipe[i-1];
                    end
                end
            end
        end
    endgenerate

    assign n_out = n_out_pipe[PIPENUM-1];
    assign e_out = e_out_pipe[PIPENUM-1];
    assign o_to_pe = o_to_pe_pipe[PIPENUM-1];

endmodule
