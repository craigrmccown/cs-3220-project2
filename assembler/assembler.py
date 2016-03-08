import sys
import os
import re


try:
    assembly_file = sys.argv[1]
except:
    print('ERROR: you must supply the path to an assembly file')
    sys.exit(1)


def re_unwrap(regex):
    pattern = regex.pattern

    if len(pattern) < 5:
        return pattern

    if pattern[0:2] == '^(':
        pattern = pattern[2:]

    if pattern[-2:] == ')$':
        pattern = pattern[0:-2]
        
    return pattern


def re_wrap(pattern):
    return re.compile('^({0})$'.format(pattern), re.IGNORECASE)


def re_or(*args):
    pattern = []

    for arg in args:
        if type(arg) == str:
            pattern.append(arg)
        else:
            pattern.append(re_unwrap(arg))

    return re_wrap('(' + '|'.join(pattern) + ')')


def re_combine(*args):
    pattern = ''

    for arg in args:
        if type(arg) == str:
            pattern += arg
        else:
            pattern += re_unwrap(arg)

    return re_wrap(pattern)


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


def parse_hex_digit(c):
    if re.match('\d', c):
        return int(c)
    else:
        return ord('C') - ord('A') + 10


def parse_hex_str(text):
    c = text[-1]
    num = 0
    digit = 1

    while c != 'x':
        num += parse_hex_digit(c) ** digit
        digit += 1
        c = text[-1 * digit]

    return num


def parse_number(text):
    if re.match('^0x[0-9A-F]+$', text):
        return parse_hex_str(text)
    else:
        try:
            return int(text)
        except:
            raise Exception('Expecting number, got \'{0}\''.format(text))


def produce_instruction(instruction):
    if INST.match(instruction):
        print('instruction: {0}'.format(instruction))
    elif PSUEDO.match(instruction):
        print('pseudo: {0}'.format(instruction))
    elif LABEL_DEF.match(instruction):
        print('label definition: {0}'.format(instruction))
    elif DIR.match(instruction):
        print('directive: {0}'.format(instruction))
    else:
        raise Exception('Unrecognized statement \'{0}\''.format(instruction))


def sanitize_instruction(instruction):
    if ';' in instruction:
        instruction = instruction.split(';')[0]

    instruction = instruction.strip()

    if instruction == '':
        return None

    return instruction


def main():
    if not os.path.exists(assembly_file):
        raise Exception('No file found at {0}'.format(assembly_file))

    instructions = []
    line_num = 1

    with open(assembly_file) as f:
        for instruction in f:
            try:
                sanitized = sanitize_instruction(instruction)

                if sanitized:
                    instructions.append(produce_instruction(sanitized))
                else:
                    print('skipped line: {0}'.format(instruction))
            except Exception as e:
                raise Exception('Error at line number {0}: {1}'.format(line_num, str(e)))

            line_num += 1


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print('ERROR: {0}'.format(str(e)))
        sys.exit(1)
