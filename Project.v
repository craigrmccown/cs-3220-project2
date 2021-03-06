module Project(
	input        CLOCK_50,
	input        RESET_N,
	input  [3:0] KEY,
	input  [9:0] SW,
	output [6:0] HEX0,
	output [6:0] HEX1,
	output [6:0] HEX2,
	output [6:0] HEX3,
	output [6:0] HEX4,
	output [6:0] HEX5,
	output [9:0] LEDR
);
	/* bit widths */
	parameter DBITS = 32;
	parameter INSTSIZE = 32'd4;
	parameter INSTBITS = 32;
	parameter REGNOBITS = 6;
	parameter IMMBITS = 14;
	parameter FUNCBITS = 4;
	parameter STARTPC = 32'h100;
	
	// I/O
	parameter ADDRHEX = 32'hFFFFF000;
	parameter ADDRLEDR = 32'hFFFFF020;
	parameter ADDRKEY = 32'hFFFFF080;
	parameter ADDRSW = 32'hFFFFF090;
	
	parameter INITFILE = "Test2.mif"; // Change this to Serter2.mif before submitting
	parameter IMEMADDRBITS = 16;
	parameter IMEMWORDBITS = 2;
	parameter IMEMWORDS = (1 << (IMEMADDRBITS - IMEMWORDBITS));
	parameter DMEMADDRBITS = 16;
	parameter DMEMWORDBITS = 2;
	parameter DMEMWORDS = (1 << (DMEMADDRBITS - DMEMWORDBITS));

	/* primary op codes */
	parameter OP1BITS = 6;
	parameter OP1_ALUR = 6'b000000;
	parameter OP1_BEQ = 6'b001000;
	parameter OP1_BLT = 6'b001001;
	parameter OP1_BLE = 6'b001010;
	parameter OP1_BNE = 6'b001011;
	parameter OP1_JAL = 6'b001100;
	parameter OP1_LW = 6'b010010;
	parameter OP1_SW = OP1_LW + 6'b001000;
	parameter OP1_ADDI = 6'b100000;
	parameter OP1_ANDI = 6'b100100;
	parameter OP1_ORI = 6'b100101;
	parameter OP1_XORI = 6'b100110;
	
	/* secondary op codes */
	parameter OP2BITS = 8;
	parameter OP2_EQ = 8'b00001000;
	parameter OP2_LT = 8'b00001001;
	parameter OP2_LE = 8'b00001010;
	parameter OP2_NE = 8'b00001011;
	parameter OP2_ADD = 8'b00100000;
	parameter OP2_AND = 8'b00100100;
	parameter OP2_OR = 8'b00100101;
	parameter OP2_XOR = 8'b00100110;
	parameter OP2_SUB = 8'b00101000;
	parameter OP2_NAND = 8'b00101100;
	parameter OP2_NOR = 8'b00101101;
	parameter OP2_NXOR = 8'b00101110;
	
	/* alu functions */
	parameter FUNC_ADD = 4'b0000;
	parameter FUNC_LT = 4'b0001;
	parameter FUNC_LE = 4'b0010;
	parameter FUNC_NE = 4'b0011;
	parameter FUNC_AND = 4'b0100;
	parameter FUNC_OR = 4'b0101;
	parameter FUNC_XOR = 4'b0110;
	/* ++additions++ */
	parameter FUNC_SUB = 4'b1000;
	parameter FUNC_NAND = 4'b1100;
	parameter FUNC_NOR = 4'b1101;
	parameter FUNC_NXOR = 4'b1110;
	

	/* pll configuration */
	wire clk,locked;

	Pll myPll(
		.refclk (CLOCK_50),
		.rst (!RESET_N),
		.outclk_0 (clk),
		.locked (locked)
	);

	wire reset = !locked;
	
	/* I/O creation */
	reg [(DBITS - 1):-] HEXout, LEDRout, KEYout, SWout;
	assign LEDR = LEDRout[9:0];
	
	//idkidk pandapandapanda
	SevenSeg Hex0Out(.hexNumIn(HEXout[3:0]), .displayOut(HEX0));
	SevenSeg Hex1Out(.hexNumIn(HEXout[7:4]), .displayOut(HEX1));
	SevenSeg Hex2Out(.hexNumIn(HEXout[11:8]), .displayOut(HEX2));
	SevenSeg Hex3Out(.hexNumIn(HEXout[15:12]), .displayOut(HEX3));


  /* bus creation */
	tri [(DBITS-1):0] thebus;
	parameter BUSZ = {DBITS{1'bZ}};

  /* pc creation */
	reg [(DBITS-1):0] PC;
	reg LdPC, DrPC, IncPC;
	
	initial begin
		PC <= {(DBITS - 9){1'b0}, 9'h100};
	end

	always @(posedge clk or posedge reset) begin
		if (reset) begin
			PC <= STARTPC;
		end else if (LdPC) begin
			PC <= thebus;
		end else if (IncPC) begin
			PC <= PC + INSTSIZE;
		end
	end

	assign thebus = DrPC ? PC : BUSZ;

	/* instruction memory creation */
	(* ram_init_file = INITFILE *)
	reg [(DBITS - 1):0] imem[(IMEMWORDS - 1):0];
	wire [(DBITS - 1):0] iMemOut = imem[PC[(IMEMADDRBITS - 1):IMEMWORDBITS]];

	/* ir creation */
	reg [(INSTBITS - 1):0] IR;
	reg LdIR;

	always @(posedge clk or posedge reset) begin
		if (reset) begin
			IR <= 32'hDEADDEAD;
		end else if (LdIR) begin
			IR <= iMemOut;
		end
	end

	/* split ir into instruction parts */
	wire[(OP1BITS - 1):0] op1;
	wire[(FUNCBITS - 1):0] op1func;
	wire[(REGNOBITS - 1):0] rd, rs, rt;
	wire[(IMMBITS - 1):0] imm;
	wire[(OP2BITS - 1):0] op2;
	wire[(FUNCBITS - 1):0] op2func;
	wire[(DBITS - 1):0] immsxt;
	
	assign op1 = IR[(INSTBITS - 1):(INSTBITS - OP1BITS)];
	assign op1func = op1[(FUNCBITS - 1):0];
	assign rs = IR[(INSTBITS - OP1BITS - 1):(INSTBITS - OP1BITS - REGNOBITS)];
	assign rt = IR[(INSTBITS - OP1BITS - REGNOBITS - 1):(INSTBITS - OP1BITS - (REGNOBITS * 2))];
	assign rd = IR[(INSTBITS - OP1BITS - (REGNOBITS * 2) - 1):(INSTBITS - OP1BITS - (REGNOBITS * 3))];
	assign op2 = IR[(INSTBITS - OP1BITS - (REGNOBITS * 3) - 1):0];
	assign op2func = op2[(FUNCBITS - 1):0];
	assign imm = IR[(INSTBITS - OP1BITS - (REGNOBITS * 2) - 1):0];
	
   /* create sxt offset */
	(.IBITS(IMMBITS), .OBITS(DBITS)) #SXT(imm, immsxt);
	reg ShOff, DrOff;
	assign immsxt = ShOff ? (immsxt << 2) : BUSZ;
	assign thebus = DrOff ? immsxt : BUSZ;
  
   /* create dmem */
	(* ram_init_file = INITFILE *)
	reg [(DBITS - 1):0] dmem[(DMEMWORDS - 1):0];
	reg [(DBITS - 1):0] MDR, MAR;
	reg WrMem, LdMAR, DrMem;
	wire [(DBITS - 1):0] dMemOut = WrMem ? BUSZ : MDR;
	
	initial begin
		assign MAR = {(DBITS - 1){1'b0}, 1'b1};
	end
	
	always @(posedge clk) begin
		MDR <= dmem[MAR]
		
		if (WrMem && !reset) begin
			dmem[MAR] <= thebus;
		end
		
		if (LdMAR && !reset) begin
			MAR <= thebus;
		end
	end

	assign thebus = DrMem ? dMemOut : BUSZ;
  
    /* create register file */
	reg [(DBITS - 1):0] regs[63:0];
	reg [(REGNOBITS - 1):0] regno;
	reg WrReg, DrReg;

	always @(posedge clk) begin
		if (WrReg && !reset) begin
			regs[regno] <= thebus;
		end
	end

	//wire [(DBITS-1):0] regOut = WrReg ? {DBITS{1'bX}} : regs[regno];
	wire [(DBITS-1):0] regOut = WrReg ? BUSZ : regs[regno];
	assign thebus = DrReg ? regOut : BUSZ;
  
	/* create ALU registers */
	reg signed [(DBITS-1):0] A, B;
	reg LdA, LdB, DrALU;
	
	/* connect A and B registers to the bus */
	always @(posedge clk or posedge reset) begin
		if (reset) begin
			{A,B} <= 32'hDEADDEAD;
		end else begin
			if (LdA) begin
				A <= thebus;
			end
			
			if (LdB) begin
				B <= thebus;
			end
		end
	end
	
	/* connect ALU output to the bus */
	reg signed [(DBITS-1):0] ALUout;
	assign thebus = DrALU ? ALUout : b;
	
	/* grab ALU func bits */
	wire [(FUNCBITS - 1):0] func;
	assign func = op1 == {OP1BITS{1'b0}} ? op2func : op1func;

	/* create ALU */
	always @(A or B) begin
		case (func)
			FUNC_ADD: ALUout = A + B;
			FUNC_LT: ALUout = (A < B) ? 32'd1 : 0;
			FUNC_LE: ALUout = (A < B or A == B) ? 32'd1 : 0;
			FUNC_NE: ALUout = (A != B) ? 32'd1 : 0;
			FUNC_AND: ALUout = A and B;
			FUNC_OR: ALUout = A or B;
			FUNC_XOR: ALUout = A ^ B;
			FUNC_SUB: ALUout = A - B;
			FUNC_NAND: ALUout = !(A and B);
			FUNC_NOR: ALUout = !(A or B);
			FUNC_NXOR: ALUout = !(A ^ B);
		endcase
	end
  
	/* micro states */
	parameter S_BITS=5;
	parameter [(S_BITS - 1):0]
		S_ZERO = {(S_BITS){1'b0}},
		S_ONE = {{(S_BITS - 1){1'b0}}, 1'b1},
		S_FETCH1 = S_ZERO,
		S_FETCH2 = S_ONE,
		S_ALUI1 = S_ONE * 2,
		S_ALUI2 = S_ONE * 3,
		S_ALUR1 = S_ONE * 4,
		S_ALUR2 = S_ONE * 5,
		S_JAL1 = S_ONE * 6,
		S_JAL2 = S_ONE * 7,
		S_JAL3 = S_ONE * 8,
		S_B1 = S_ONE * 9,
		S_B2 = S_ONE * 10,
		S_B3 = S_ONE * 11,
		S_B4 = S_ONE * 12,
		S_B5 = S_ONE * 13,
		S_S1 = S_ONE * 14,
		S_S2 = S_ONE * 15,
		S_S3 = S_ONE * 16,
		S_L1 = S_ONE * 17,
		S_L2 = S_ONE * 18,
		S_L3 = S_ONE * 19;
		S_ERROR = S_ONE * 20;

	reg [(S_BITS-1):0] state, next_state;
	
	always @(state or op1 or rs or rt or rd or op2 or ALUout[0]) begin
		{LdPC, DrPC, IncPC, LdMAR, WrMem, DrMem, LdIR, DrOff, ShOff, LdA, LdB, ALUfunc, DrALU, regno, DrReg, WrReg, next_state} =
		{1'b0, 1'b0, 1'b0, 1'b0, 1'b0, 1'b0, 1'b0, 1'b0, 1'b0, 1'b0, 1'b0, 6'bX, 1'b0, 6'bX, 1'b0, 1'b0, state + S_ONE};
		
		case (state)
			S_FETCH1: begin
				{LdIR, IncPC} = {1'b1,1'b1};
			end
			S_FETCH2: begin
				case(op1)
					OP1_ALUR: begin
						case(op2)
							OP2_ADD, OP2_SUB,
							OP2_EQ, OP2_LT, OP2_LE, OP2_NE,
							OP2_AND, OP2_OR, OP2_XOR,
							OP2_NAND, OP2_NOR, OP2_NXOR
								next_state = S_ALUR1;
							default: next_state = S_ERROR;
						endcase
					end
					OP1_ADDI, OP1_ANDI,
					OP1_ORI, OP1_XORI: begin
						next_state = S_ALUI1;
					end
					OP1_BEQ, OP1_BLT, OP1_BLE, OP1_BNE begin
						next_state = S_B1;
					end
					OP1_JAL: begin
						next_state = S_JALR1;
					end
					OP1_S: begin
						next_state = S_SW1;
					end
					OP1_L: begin
						next_state = S_LD1;
					default: next_state = S_ERROR;
				endcase
				{LdA, LdB, regno, DrReg} = {1'b1, 1'b1, rs, 1'b1};
			end
			S_ALUI1: begin
				{LdB, ShOff, DrOff} = {1'b1, 1'b1, 1'b1};
				next_state = ALUI2;
			end
			S_ALUI2: begin
				{ALUfunc, DrALU, regno, WrReg} = {op2func, 1'b1, rt, 1'b1};
				next_state = S_FETCH1;
			end
			S_ALUR1: begin
				{LdB, regno, DrReg} = {1'b1, rt, 1'b1};
				next_state = ALUR2;
			end
			S_ALUR2: begin
				{ALUfunc, DrALU, regno, WrReg} = {op2func, 1'b1, rd, 1'b1};
				next_state = S_FETCH1;
			end
			S_JALR1: begin
				{regno, WrReg, DrPC} = {rt, 1'b1, 1'b1};
				next_state = S_JALR2;
			end
			S_JAL2 begin
				{LdB, ShOff, DrOff} = {1'b1, 1'b1, 1'b1};
				next_state = S_JAL3;
			end
			S_JAL3 begin
				{ALUfunc, DrALU, LdPC} = {FUNC_ADD, 1'b1, 1'b1};
				next_state = S_FETCH1;
			end
			S_B1: begin
				{LdB, regno, DrReg} = {1'b1, rt, 1'b1};
				next_state = S_B2;
			end
			S_B2: begin
				{ALUfunc, DrALU} = {op1func, 1'b1};
				if (!ALUout) begin
					next_state = S_FETCH1;
				end else begin
					next_state = S_B3;
				end
			end
			S_B3: begin
				{LdA, DrPC} = {1'b1, 1'b1};
				next_state = S_B4;
			end
			S_B4: begin
				{LdB, ShOff, DrOff} = {1'b1, 1'b1, 1'b1};
				next_state = S_B5;
			end
			S_B5: begin
				{LdPC, ALUfunc, DrALU} = {1'b1, op1func, 1'b1};
				next_state = S_FETCH1;
			end
			S_S1: begin
				{LdB, DrOff} = {1'b1, 1'b1}; 
				next_state = S_S2;
			end
			S_S2: begin
				{ALUfunc, DrALU, LdMAR} = {op1func, 1'b1, 1'b1};
				next_state = S_S3;
			end
			S_S3: begin
				{regno, WrMem, DrReg} = {rt, 1'b1, 1'b1};
				next_state = S_FETCH1;
			end
			S_L1: begin
				{LdB, DrOff} = {1'b1, 1'b1}; 
				next_state = S_L2;
			end
			S_L2: begin
				{ALUfunc, DrALU, LdMAR} = {op1func, 1'b1, 1'b1};
				next_state = S_L3;
			end
			S_L3: begin
				{DrMem, regno, WrReg} = {1'b1, rt, 1'b1};
				next_state = S_FETCH1;
			default: next_state=S_ERROR;
		endcase
	end
	
	always @(posedge clk or posedge reset) begin
		if(reset) begin
			state <= S_FETCH1;
		end else begin
			state <= next_state;
		end
	end
endmodule

module SXT(IN,OUT);
	parameter IBITS;
	parameter OBITS;
	input  [(IBITS-1):0] IN;
	output [(OBITS-1):0] OUT;
	assign OUT = {{(OBITS-IBITS){IN[IBITS-1]}},IN};
endmodule
