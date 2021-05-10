`include "mocarabe.h"
`include "benchmark.h"

//pe with 2 inputs, suitable for C > 1
module pe_2_input #(
    parameter SCHED_LEN = 16,
    parameter X_MAX     = 4,
    parameter Y_MAX     = 4,
    parameter X     = 0,    // X address of this node
    parameter Y     = 0,    // Y address of this node
    parameter OP = 0, // 0 = +, 1 = *
    parameter PIPE = 5
) (
    input  wire clk,        // clock
    input wire `D_WIDTH i_operand0, //1st input from Noc
    input wire `D_WIDTH i_operand1, //2nd input from Noc
    output reg done_a_pe,
    output wire `D_WIDTH result
);
    // Processing Element

    wire `D_WIDTH op1;
    wire `D_WIDTH op2;

    reg `D_WIDTH op1_reg;
    reg `D_WIDTH op2_reg;
    reg `D_WIDTH result_pipe [PIPE-1 : 0];
    localparam NOW_BITWIDTH = SCHED_LEN==1? 1: $clog2(SCHED_LEN);
    // bitwidth of schedule.  SCHED_LEN=II if II constraint is on
    reg [NOW_BITWIDTH-1:0] now=0; //bitwidth of schedule

    // 1) FIFO for inputs
    // op1 fifo
     reg [$clog2(`FIFO_DEPTH)-1:0] op1_addr_memory `SCHED;
     reg [$clog2(`FIFO_DEPTH)-1:0] op2_addr_memory `SCHED;
     reg [$clog2(`FIFO_DEPTH)-1:0] op1_addr;
     reg [$clog2(`FIFO_DEPTH)-1:0] op2_addr;

    reg [31:0] global_cycle;
    //op1 fifo
    pe_srl #(.WIDTH(`BENCHMARK_DATA_WIDTH), .FIFO_DEPTH(`FIFO_DEPTH), .X(X), .Y(Y))
        srl_inst_op1 (.clk(clk),
                    .wr(1'b1), .wrdata(i_operand0),
                    .raddr(op1_addr),
                    //.waddr(now),
                    .rddata(op1)
        );

    //op2 fifo
    pe_srl #(.WIDTH(`BENCHMARK_DATA_WIDTH), .FIFO_DEPTH(`FIFO_DEPTH), .X(X), .Y(Y))
        srl_inst_op2 (.clk(clk),
                    .wr(1'b1), .wrdata(i_operand1),
                    .raddr(op2_addr),
                    //.waddr(now),
                    .rddata(op2)
        );


    integer pe_init;
    initial begin
        $readmemh($sformatf("op1_addr_memory_x%0d_y%0d.dat", X, Y), op1_addr_memory);
        $readmemh($sformatf("op2_addr_memory_x%0d_y%0d.dat", X, Y), op2_addr_memory);
        done_a_pe = 0;
        global_cycle = 0;

        for (pe_init = 0; pe_init < PIPE; pe_init = pe_init + 1) begin : initialize_pe
            result_pipe[pe_init] = 0;
        end
    end



    always @(posedge clk) begin
        // don't bother resetting

        // we register op1 and op2
        op1_reg <= op1;
        op2_reg <= op2;
        if( OP == 0 ) begin
            result_pipe[0] <= op1_reg + op2_reg;
        end
        else if (OP == 1) begin
            result_pipe[0] <= op1_reg * op2_reg;
        end
        else if ( OP == 2) begin//IO PE
            result_pipe[0] <=  (100*(X+Y*X_MAX)) + global_cycle;
        end
        global_cycle <= global_cycle + 1;
        // $display("global cycle: %0d\n",global_cycle);
        // $display("@%0d: op1 addr: %0b, op1: %0d; op2 addr: %0b, op2: %0d", now, op1_addr, op1, op2_addr, op2);

        // if( op1 != {`BENCHMARK_DATA_WIDTH{1'b0}} || op2 != {`BENCHMARK_DATA_WIDTH{1'b0}} )
        //     $display("(%0d, %0d), t=%0d: %0d + %0d = %0d",X, Y, now, op1, op2, result_pipe[0] );
        // $display("@%0d: (%0d, %0d): result: %0d.  i_operand0: %0d, i_operand1: %0d. ", now, X, Y, result,i_operand0,i_operand1);
        op1_addr <= op1_addr_memory[now];
        op2_addr <= op2_addr_memory[now];
        if( now == SCHED_LEN - 1 )
            now <= 0;
        else
            now <= now + 1;
        if( now >= 8 )
            done_a_pe = 1;
        $display("@g%0d, (%0d,%0d) i_operand0: %0d, i_operand1: %0d, computed %0d, outputting %0d", global_cycle, X, Y, i_operand0, i_operand1,result_pipe[0], result_pipe[PIPE-1]);

    end


    genvar i;
    generate
        for(i = 1; i < PIPE; i = i + 1)begin
            always @(posedge clk) begin
                 result_pipe[i] <= result_pipe[i-1];
            end
        end
    endgenerate

    assign result = result_pipe[PIPE-1];

endmodule

