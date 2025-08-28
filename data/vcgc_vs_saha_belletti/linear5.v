module top( x0 , x1 , x2 , x3 , x4 , y0 );
  input x0 , x1 , x2 , x3 , x4 ;
  output y0 ;
  wire n6 , n7 , n8 , n9 , n10 , n11 , n12 ;
  assign n6 = x1 ^ x0 ;
  assign n7 = x2 ^ x1 ;
  assign n8 = n6 & n7 ;
  assign n9 = x3 ^ x2 ;
  assign n10 = n8 & n9 ;
  assign n11 = x4 ^ x3 ;
  assign n12 = n10 & n11 ;
  assign y0 = n12 ;
endmodule
