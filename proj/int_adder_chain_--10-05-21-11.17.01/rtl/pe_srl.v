`include "benchmark.h"

module pe_srl #(
    parameter WIDTH = 1,
    parameter FIFO_DEPTH = 4,
    parameter X = 0,
    parameter Y = 0
) (
    input clk,
    // input rst,
    input [WIDTH-1:0] wrdata,
    input wr,
    // input ce,
    input [$clog2(`FIFO_DEPTH)-1:0] raddr,
    output [WIDTH-1:0] rddata
    );

    // Only generate one of these three

    genvar i;
    generate if (FIFO_DEPTH <= 16) begin : srl_16_logic
    ///// SRL16 instance
    for (i = 0; i < WIDTH; i=i+1) begin : srl16
        SRL16E fifo16(
            .CLK(clk),
            .CE(wr),
            .D(wrdata[i]),
            .A0(raddr[0]),
            .A1(raddr[1]),
            .A2(raddr[2]),
            .A3(raddr[3]),
            .Q(rddata[i])
            );
    end
    end endgenerate

    genvar j;
    generate if (FIFO_DEPTH > 16 && FIFO_DEPTH <= 32) begin : srl_32_logic
    ///// SRL32 instance
    for (j = 0; j < WIDTH; j=j+1) begin : srl32
        SRLC32E fifo32(
          .CLK(clk),
          .CE(wr),
          .D(wrdata[j]),
          .A(raddr[4:0]),
          .Q(rddata[j]),
          .Q31());
    end
    end endgenerate

    genvar k;
    generate if (FIFO_DEPTH > 32) begin : srl_64_logic
    ///// SRL64 instance
    for (k = 0; k < WIDTH; k=k+1) begin : srl64
        SRL64 fifo64(
          .CLK(clk),
          .CE(wr),
          .D(wrdata[k]),
          .A(raddr[5:0]),
          .Q(rddata[k]),
          .Q63());
    end
  end endgenerate

endmodule
