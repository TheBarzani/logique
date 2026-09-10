module top(a, b, c, y);
input a, b, c;
output y;
wire p;
assign p = a ^ b;
assign y = p & c;
endmodule
