from regex import re_wrap, re_unwrap, re_or, re_combine
import re

SPACE = re_wrap('\s+')
OPTIONAL_SPACE = re_wrap('\s*')
COMMENT = re_wrap(';.*')
DECIMAL = re_wrap('-?\d+')
HEX = re_wrap('0x[0-9A-F]+')
NUMBER = re_or(DECIMAL, HEX)
IDENTIFIER = re_wrap('\w+')
ORIG = re_wrap('\.ORIG')
WORD = re_wrap('\.WORD')
NAME = re_wrap('\.NAME')
KV_PAIR = re_combine(IDENTIFIER, OPTIONAL_SPACE, '=', OPTIONAL_SPACE, NUMBER)
DIR_ORIG = re_combine(ORIG, SPACE, NUMBER)
DIR_WORD = re_combine(WORD, SPACE, IDENTIFIER)
DIR_NAME = re_combine(NAME, SPACE, KV_PAIR)
DIR = re_or(DIR_ORIG, DIR_WORD, DIR_NAME)
LABEL_DEF = re_combine(IDENTIFIER, ':')
REG_ZERO = re_wrap('Zero')
REG_RV = re_wrap('RV')
REG_RA = re_wrap('RA')
REG_SP = re_wrap('SP')
REG_GP = re_wrap('GP')
REG_FP = re_wrap('FP')
REG_A = re_wrap('A[0-9]|A1[0-5]')
REG_T = re_wrap('T[0-9]|T1[0-5]')
REG_S = re_wrap('S[0-9]|S1[0-5]')
REG = re_or(REG_ZERO, REG_RV, REG_RA, REG_SP, REG_GP, REG_FP, REG_A, REG_T, REG_S)
IMM = re_or(IDENTIFIER, NUMBER)
IMM_REG = re_combine(IMM, '\(', REG, '\)')
OP_BEQ = re_wrap('BEQ')
OP_BLT = re_wrap('BLT')
OP_BLE = re_wrap('BLE')
OP_BNE = re_wrap('BNE')
OP_JAL = re_wrap('JAL')
OP_LB = re_wrap('LB')
OP_LH = re_wrap('LH')
OP_LW = re_wrap('LW')
OP_LD = re_wrap('LD')
OP_LBU = re_wrap('LBU')
OP_LHU = re_wrap('LHU')
OP_LWU = re_wrap('LWU')
OP_SB = re_wrap('SB')
OP_SH = re_wrap('SH')
OP_SW = re_wrap('SW')
OP_SD = re_wrap('SD')
OP_ADDI = re_wrap('ADDI')
OP_ANDI = re_wrap('ANDI')
OP_ORI = re_wrap('ORI')
OP_XORI = re_wrap('XORI')
OP_ADD = re_wrap('ADD')
OP_AND = re_wrap('AND')
OP_OR = re_wrap('OR')
OP_XOR = re_wrap('XOR')
OP_SUB = re_wrap('SUB')
OP_NAND = re_wrap('NAND')
OP_NOR = re_wrap('NOR')
OP_NXOR = re_wrap('NXOR')
OP_EQ = re_wrap('EQ')
OP_LT = re_wrap('LT')
OP_LE = re_wrap('LE')
OP_NE = re_wrap('NE')
OP_BRANCH = re_or(OP_BEQ, OP_BLT, OP_BLE, OP_BNE)
OP_LOAD = re_or(OP_LB, OP_LH, OP_LW, OP_LD, OP_LBU, OP_LHU, OP_LWU)
OP_STORE = re_or(OP_SB, OP_SH, OP_SW, OP_SD)
OP_FUNCI = re_or(OP_ADDI, OP_ANDI, OP_ORI, OP_XORI)
OP_FUNCR = re_or(OP_ADD, OP_AND, OP_OR, OP_XOR, OP_SUB, OP_NAND, OP_NOR, OP_NXOR, OP_EQ, OP_LT, OP_LE, OP_NE)
PS_NOT = re_combine('NOT', SPACE, REG, ',', REG)
PS_CALL = re_combine('CALL', SPACE, IMM_REG)
PS_RET = re_wrap('RET')
PS_JMP = re_combine('JMP', SPACE, IMM_REG)
PS_BGT = re_combine('BGT', SPACE, REG, ',', REG, ',', IDENTIFIER)
PS_BGE = re_combine('BGE', SPACE, REG, ',', REG, ',', IDENTIFIER)
PS_BR = re_combine('BR', SPACE, IDENTIFIER)
PS_GT = re_combine('GT', SPACE, REG, ',', REG, ',', REG)
PS_GE = re_combine('GE', SPACE, REG, ',', REG, ',', REG)
PS_SUBI = re_combine('SUBI', SPACE, REG, ',', REG, ',', IMM)
PSUEDO = re_or(PS_NOT, PS_CALL, PS_RET, PS_JMP, PS_BGT, PS_BGE, PS_BR, PS_GT, PS_GE, PS_SUBI)
INST_JUMP = re_combine(OP_JAL, SPACE, REG, ',', IMM_REG)
INST_BRANCH = re_combine(OP_BRANCH, SPACE, REG, ',', REG, ',', IDENTIFIER)
INST_LOAD = re_combine(OP_LOAD, SPACE, REG, ',', IMM_REG)
INST_STORE = re_combine(OP_STORE, SPACE, REG, ',', IMM_REG)
INST_FUNCI = re_combine(OP_FUNCI, SPACE, REG, ',', REG, ',', IMM)
INST_FUNCR = re_combine(OP_FUNCR, SPACE, REG, ',', REG, ',', REG)
INST = re_or(INST_JUMP, INST_BRANCH, INST_LOAD, INST_STORE, INST_FUNCI, INST_FUNCR)


class ParseException(Exception):
    pass


class Token(object):
    def __init__(self, value, tokens=None):
        self.value = value
        self.tokens = tokens
        self.token_types = []


    def add_type(self, token_type):
        self.token_types.append(token_type)


    def is_type(self, token_type):
        return token_type in self.token_types


def split_on_spaces(text):
    return [x for x in re.split('\s', text) if x.strip()]


def parse_decimal(text):
    try:
        token = Token(int(text))
    except:
        raise ParseException('Expecting number, got \'{0}\''.format(text))

    token.add_type(DECIMAL)
    return token


def parse_hex_digit(c):
    if re.match('\d', c):
        return int(c)
    else:
        return ord('C') - ord('A') + 10


def parse_hex(text):
    c = text[-1]
    num = 0
    digit = 1

    while c != 'x':
        num += parse_hex_digit(c) ** digit
        digit += 1
        c = text[-1 * digit]

    token = Token(num)
    token.add_type(HEX)
    return token


def parse_number(text):
    if HEX.match(text):
        token = parse_hex(text)
    else:
        token = parse_decimal(text)

    token.add_type(NUMBER)
    return token


def parse_identifier(text):
    token = Token(text)
    token.add_type(IDENTIFIER)
    return token


def parse_imm(text):
    if NUMBER.match(text):
        token = parse_number(text)
    else:
        token = parse_identifier(text)

    token.add_type(IMM)
    return token


def parse_reg(text):
    if REG_ZERO.match(text):
        token = Token(0)
        token.add_type(REG_ZERO)
    elif REG_RV.match(text):
        token = Token(1)
        token.add_type(REG_RV)
    elif REG_RA.match(text):
        token = Token(2)
        token.add_type(REG_RA)
    elif REG_SP.match(text):
        token = Token(3)
        token.add_type(REG_SP)
    elif REG_GP.match(text):
        token = Token(4)
        token.add_type(REG_GP)
    elif REG_FP.match(text):
        token = Token(5)
        token.add_type(REG_FP)
    elif REG_A.match(text):
        token = Token(int(text[1:]) + 16)
        token.add_type(REG_A)
    elif REG_T.match(text):
        token = Token(int(text[1:]) + 32)
        token.add_type(REG_T)
    elif REG_S.match(text):
        token = Token(int(text[1:]) + 48)
        token.add_type(REG_S)
    else:
        raise ParseException('Register parse failure')

    token.add_type(REG)
    return token


def parse_imm_reg(text):
    text = text[0:len(text) - 1].split('(')
    imm_token = parse_imm(text[0])
    reg_token = parse_reg(text[1])
    token = Token(None, (imm_token, reg_token))
    token.add_type(IMM_REG)
    return token


def parse_dir_orig(text):
    split = split_on_spaces(text)
    orig_token = Token(split[0])
    orig_token.add_type(ORIG)
    number_token = parse_number(split[1])
    token = Token(None, (orig_token, number_token))
    token.add_type(DIR_ORIG)
    return token


def parse_dir_word(text):
    split = split_on_spaces(text)
    word_token = Token(split[0])
    word_token.add_type(WORD)
    identifier_token = parse_identifier(split[1])
    token = Token(None, (word_token, identifier_token))
    token.add_type(DIR_WORD)
    return token


def parse_dir_name(text):
    split = split_on_spaces(text)
    pair = [key_or_value.strip() for key_or_value in ''.join(split[1:]).split('=')]
    name_token = Token(split[0])
    name_token.add_type(NAME)
    identifier_token = parse_identifier(pair[0])
    number_token = parse_number(pair[1])
    token = Token(None, (name_token, identifier_token, number_token))
    token.add_type(DIR_NAME)
    return token


def parse_dir(text):
    if DIR_ORIG.match(text):
        token = parse_dir_orig(text)
    elif DIR_WORD.match(text):
        token = parse_dir_word(text)
    elif DIR_NAME.match(text):
        token = parse_dir_name(text)
    else:
        raise ParseException('Directive parse failure')

    token.add_type(DIR)
    return token


def parse_label_def(text):
    label = text.strip(':')
    identifier_token = parse_identifier(label)
    token = Token(None, (identifier_token,))
    token.add_type(LABEL_DEF)
    return token


def parse_pseudo(text):
    split = split_on_spaces(text)
    op = split[0]
    args = split[1].split(',')
    print(text)
    print(split)
    print(split[1])
    print(args)

    if PS_NOT.match(text):
        instruction = 'NAND {0},{1},{1}'.format(args[0], args[1])
    elif PS_CALL.match(text):
        instruction = 'JAL RA,{0}'.format(args[0])
    elif PS_RET.match(text):
        instruction = 'JAL R6,0(RA)'
    elif PS_JMP.match(text):
        instruction = 'JAL R6,{0}'.format(args[0])
    elif PS_BGT.match(text):
        instruction = 'BGT {0},{1},{2}'.format(args[1], args[0], args[2])
    elif PS_BGE.match(text):
        instruction = 'BLE {0},{1},{2}'.format(args[1], args[0], args[2])
    elif PS_BR.match(text):
        instruction = 'BEQ Zero,Zero,{0}'.format(args[0])
    elif PS_GT.match(text):
        instruction = 'LT {0},{1},{2}'.format(args[0], args[2], args[1])
    elif PS_GE.match(text):
        instruction = 'LE {0},{1},{2}'.format(args[0], args[2], args[1])
    elif PS_SUBI.match(text):
        instruction = 'ADDI {0},{1},{2}'.format(args[0], args[1], '-' + args[2])
    else:
        raise ParseException('Pseudo parse failure')


    return parse_instruction(instruction)


def parse_instruction(text):
    split = split_on_spaces(text)
    op = split[0]
    args = split[1].split(',')
    op_token = Token(op)

    if INST_JUMP.match(text):
        op_token.add_type(OP_JAL)
        reg_token = parse_reg(args[0])
        imm_reg_token = parse_imm_reg(args[1])
        children = (op_token, reg_token, imm_reg_token)
    elif INST_BRANCH.match(text):
        for branch_op in [OP_BEQ, OP_BLT, OP_BLE, OP_BNE]:
            if branch_op.match(op):
                op_token.add_type(branch_op)

        reg_token1 = parse_reg(args[0])
        reg_token2 = parse_reg(args[1])
        identifier_token = parse_identifier(args[2])
        children = (reg_token1, reg_token2, identifier_token)
    elif INST_LOAD.match(text):
        for load_op in [OP_LB, OP_LH, OP_LW, OP_LD, OP_LBU, OP_LHU, OP_LWU]:
            if load_op.match(op):
                op_token.add_type(load_op)

        reg_token = parse_reg(args[0])
        imm_reg_token = parse_imm_reg(args[1])
        children = (reg_token, imm_reg_token)
    elif INST_STORE.match(text):
        for store_op in [OP_SB, OP_SH, OP_SW, OP_SD]:
            if store_op.match(op):
                op_token.add_type(store_op)

        reg_token = parse_reg(args[0])
        imm_reg_token = parse_imm_reg(args[1])
        children = (reg_token, imm_reg_token)
    elif INST_FUNCI.match(text):
        for func_op in [OP_ADDI, OP_ANDI, OP_ORI, OP_XORI]:
            if func_op.match(op):
                op_token.add_type(func_op)

        reg_token1 = parse_reg(args[0])
        reg_token2 = parse_reg(args[1])
        imm_token = parse_imm(args[2])
        children = (reg_token1, reg_token2, imm_token)
    elif INST_FUNCR.match(text):
        for func_op in [OP_ADD, OP_AND, OP_OR, OP_XOR, OP_SUB, OP_NAND, OP_NOR, OP_NXOR, OP_EQ, OP_LT, OP_LE, OP_NE]:
            if func_op.match(op):
                op_token.add_type(func_op)

        reg_token1 = parse_reg(args[0])
        reg_token2 = parse_reg(args[1])
        reg_token3 = parse_reg(args[2])
        children = (reg_token1, reg_token2, reg_token3)
    else:
        raise ParseException('Instruction parse failure')

    token = Token(None, children)
    token.add_type(INST)
    return token


def parse_line(text):
    if INST.match(text):
        return parse_instruction(text)
    elif PSUEDO.match(text):
        return parse_pseudo(text)
    elif LABEL_DEF.match(text):
        return parse_label_def(text)
    elif DIR.match(text):
        return parse_dir(text)
    else:
        raise ParseException('Unrecognized statement \'{0}\''.format(text))
