module and_with_nand(
	output out, 
	input a, 
	input b); 

wire anandb; 
nand nand1(anandb, a, b); 
nand nand2(out, anandb, anandb); 

endmodule

