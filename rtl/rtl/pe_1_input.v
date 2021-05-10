`include "mocarabe.h"
`include "benchmark.h"

//pe with one input, suitable for C=1
module pe_1_input #(
    parameter SCHED_LEN = 16,
    parameter X_MAX     = 4,
    parameter Y_MAX     = 4,
    parameter X     = 0,    // X address of this node
    parameter Y     = 0,    // Y address of this node
    parameter OP = 0, // 0 = +, 1 = *
    parameter PIPE = 5
) (
    input  wire clk,        // clock
    input wire `D_WIDTH i_operand, //input from Noc
    output reg done_a_pe,
    output wire `D_WIDTH result
);
    // Processing Element

    wire `D_WIDTH op1;
    wire `D_WIDTH op2;

    reg `D_WIDTH op1_reg;
    reg `D_WIDTH op2_reg;

    // reg `D_WIDTH result_stage1;
    // reg `D_WIDTH result_stage2;
    // reg `D_WIDTH result_stage3;
    // reg `D_WIDTH result_stage4;
    reg `D_WIDTH result_pipe [PIPE-1 : 0];
        // bitwidth of schedule.  SCHED_LEN=II if II constraint is on
    reg [$clog2(SCHED_LEN)-1:0] now=0; //bitwidth of schedule

    // 1) FIFO for inputs
    // op1 fifo
     reg [$clog2(SCHED_LEN)-1:0] op1_addr_memory `SCHED;
     reg [$clog2(SCHED_LEN)-1:0] op2_addr_memory `SCHED;
     reg [$clog2(SCHED_LEN)-1:0] op1_addr;
     reg [$clog2(SCHED_LEN)-1:0] op2_addr;

    pe_srl #(.WIDTH(`BENCHMARK_DATA_WIDTH), .SCHED_LEN(SCHED_LEN), .X(X), .Y(Y))
        srl_inst_op1 (.clk(clk),
                    .wr(1'b1), .wrdata(i_operand),
                    .raddr(op1_addr),
                    .waddr(now),
                    .rddata(op1)
        );
    //op2 fifo
    pe_srl #(.WIDTH(`BENCHMARK_DATA_WIDTH), .SCHED_LEN(SCHED_LEN), .X(X), .Y(Y))
        srl_inst_op2 (.clk(clk),
                    .wr(1'b1), .wrdata(i_operand),
                    .raddr(op2_addr),
                    .waddr(now),
                    .rddata(op2)
        );

    reg `D_WIDTH input_operand_fifo `SCHED;

    initial begin

        $display("Loading PE(%0d,%0d) input_operand_fifo",X,Y);
        $readmemh("operand_fifo.dat", input_operand_fifo);

        $display("Loading PE(%0d,%0d) op1 schedule",X,Y);
        $readmemb("op1_addr_memory_4cycles.dat", op1_addr_memory);

        $display("Loading PE(%0d,%0d) op2 schedule",X,Y);
        $readmemb("op2_addr_memory_4cycles.dat", op2_addr_memory);

        done_a_pe = 0;
    end

    always @(posedge clk) begin
        // don't bother resetting

        // we register op1 and op2
        op1_reg <= op1;
        op2_reg <= op2;

        // if( OP == 0 ) begin
        //     result_stage1 <= op1_reg + op2_reg;
        // end
        // else begin
        //     result_stage1 <= op1_reg * op2_reg;
        // end
        // result_stage2 <= result_stage1;
        // result_stage3<= result_stage2;
        // result_stage4<=result_stage3;
        // result <= result_stage4;
        if( OP == 0 ) begin
            result_pipe[0] <= op1_reg + op2_reg;
        end
        else begin
            result_pipe[0] <= op1_reg * op2_reg;
        end

        $display("@%0d: op1 addr: %0b, op1: %0d; op2 addr: %0b, op2: %0d", now, op1_addr, op1, op2_addr, op2);
        if( op1 != {`BENCHMARK_DATA_WIDTH{1'b0}} || op2 != {`BENCHMARK_DATA_WIDTH{1'b0}} )
            $display("(%0d, %0d), t=%0d: %0d + %0d = %0d",X, Y, now, op1, op2, result );

        op1_addr <= op1_addr_memory[now];
        op2_addr <= op2_addr_memory[now];
        now <= now + 1;

        if( now >= 8 )
            done_a_pe = 1;

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

