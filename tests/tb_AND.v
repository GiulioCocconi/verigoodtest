// This file was autogenerated by verigoodtest, if you find any bug please open an issue on github
module tb_AND;

// Pins
reg A;
reg B;
wire O;

AND dut(.A(A), .B(B), .O(O));

// Truth table
initial begin
A = 0; B = 0; 
#10 A = 0; B = 1; 
#10 A = 1; B = 0; 
#10 A = 1; B = 1; 
end

initial begin
$monitor("simtime = %g, \tA = %b, \tB = %b, \tO = %b, ", $time, A, B, O);
end


endmodule
