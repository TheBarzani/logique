module top( x0 , x1 , x2 , x3 , x4 , x5 , y0 );
  input x0 , x1 , x2 , x3 , x4 , x5 ;
  output y0 ;
  wire n7 , n8 , n9 , n10 , n11 , n12 , n13 , n14 , n15 , n16 , n17 , n18 , n19 ;
  assign n7 = x1 ^ x0 ;
  assign n8 = x3 ^ x0 ;
  assign n9 = n7 & n8 ;
  assign n10 = x2 ^ x1 ;
  assign n11 = n9 & n10 ;
  assign n12 = x4 ^ x1 ;
  assign n13 = n11 & n12 ;
  assign n14 = x5 ^ x2 ;
  assign n15 = n13 & n14 ;
  assign n16 = x4 ^ x3 ;
  assign n17 = n15 & n16 ;
  assign n18 = x5 ^ x4 ;
  assign n19 = n17 & n18 ;
  assign y0 = n19 ;
endmodule
