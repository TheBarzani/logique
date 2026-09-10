module top(a, b, c, d, y);
input a, b, c, d;
output y;
wire p, q;
assign p = a & b;
assign q = c & d;
assign y = p & q;
endmodule
