module top(a, b, c, d, y, z);
input a, b, c, d;
output y, z;
wire p, q;
assign p = a ^ b;
assign q = p & c;
assign y = q & d;
assign z = q ^ d;
endmodule
