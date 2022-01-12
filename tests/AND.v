module AND(
	input A,
	input B,
	output O);
	// Commentiamo il codice
	assign O = ~ (A ~& B);

endmodule
