`timescale 1ns / 1ps

module SRL64 #(
    parameter bit [63:0] INIT = 64'h0000000000000000
)(
    output wire Q,
    output wire Q63,
    input  wire [5:0] A,
    input  wire CE,
    input  wire CLK,
    input  wire D
);

    // Declaration-site initialization: Works in Xilinx Vivado, Slang, Yosys & Quartus
    reg [63:0] data = INIT;

    assign Q   = data[A];
    assign Q63 = data[63];

    always @(posedge CLK) begin
        if (CE) begin
            data <= {data[62:0], D};
        end
    end

endmodule