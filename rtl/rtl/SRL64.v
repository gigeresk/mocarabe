// made this up for simulation...
`timescale  1 ps / 1 ps


module SRL64 (Q, Q63, A, CE, CLK, D);

    parameter INIT = 64'h0000000000000000;

    output Q;
    output Q63;

    input  [5:0] A;
    input  CE, CLK, D;

    reg  [63:0] data;


    assign  Q = data[A];
    assign  Q63 = data[63];

    initial
    begin
          assign  data = INIT;
          while (CLK === 1'b1 || CLK===1'bX)
            #10;
          deassign data;
    end

  always @(posedge CLK)
    if (CE == 1'b1)
      data <= {data[62:0], D};


endmodule



