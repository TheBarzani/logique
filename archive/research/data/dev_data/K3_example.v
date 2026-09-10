module top( x0 , x1 , x2 , x3 , x4 , x5 , y0 );
  input x0 , x1 , x2 , x3 , x4 , x5 ;
  output y0 ;
  wire n7 , n8 , n9 , n10 , n11 , n12 , n13 , n14 , n15 , n16 , n17 ;
  assign n7 = x2 ^ x0 ;
  assign n8 = x3 ^ x1 ;
  assign n9 = ~n7 & ~n8 ;
  assign n10 = x4 ^ x0 ;
  assign n11 = x5 ^ x1 ;
  assign n12 = ~n10 & ~n11 ;
  assign n13 = ~n9 & ~n12 ;
  assign n14 = x4 ^ x2 ;
  assign n15 = x5 ^ x3 ;
  assign n16 = ~n14 & ~n15 ;
  assign n17 = n13 & ~n16 ;
  assign y0 = n17 ;
endmodule
