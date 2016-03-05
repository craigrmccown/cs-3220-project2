module ALU(OUT, A, B, FUNC);
	parameter DBITS;
	parameter FUNC_ADD = 3'b000;
	parameter FUNC_AND = 3'b100;
	parameter FUNC_OR = 3'b101;
	parameter FUNC_XOR = 3'b110;
	
	output [(DBITS - 1):0] OUT;
	input [(DBITS - 1):0] A, B;
	input [2:0] FUNC;
	
	always @(A or B) begin
		case (FUNC)
			FUNC_ADD: OUT = A + B;
			FUNC_AND: OUT = A and B;
			FUNC_OR: OUT = A or B;
			FUNC_XOR: OUT = A ^ B;
		endcase
	end
endmodule
