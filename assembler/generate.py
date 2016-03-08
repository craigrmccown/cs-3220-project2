import parse


labels = {}
names = {}


def get_primary_opcode(op_token):
    if op_token.is_type(parse.OP_JAL):
        return 0B001100
    elif op_token.is_type(parse.OP_BEQ):
        return 0B001000
    elif op_token.is_type(parse.OP_BLT):
        return 0B001001
    elif op_token.is_type(parse.OP_BLE):
        return 0B001010
    elif op_token.is_type(parse.OP_BNE):
        return 0B001011
    elif op_token.is_type(parse.OP_LB):
        return 0B010000
    elif op_token.is_type(parse.OP_LH):
        return 0B010001
    elif op_token.is_type(parse.OP_LW):
        return 0B010010
    elif op_token.is_type(parse.OP_LD):
        return 0B010011
    elif op_token.is_type(parse.OP_LBU):
        return 0B010100
    elif op_token.is_type(parse.OP_LHU):
        return 0B010101
    elif op_token.is_type(parse.OP_LWU):
        return 0B010110
    elif op_token.is_type(parse.OP_SB):
        return 0B011000
    elif op_token.is_type(parse.OP_SH):
        return 0B011001
    elif op_token.is_type(parse.OP_SW):
        return 0B011010
    elif op_token.is_type(parse.OP_SD):
        return 0B011011
    elif op_token.is_type(parse.OP_ADDI):
        return 0B100000
    elif op_token.is_type(parse.OP_ANDI):
        return 0B100100
    elif op_token.is_type(parse.OP_ORI):
        return 0B100101
    elif op_token.is_type(parse.OP_XORI):
        return 0B100110
    else:
        raise Exception('Unrecognized primary opcode')


def get_secondary_opcode(op_token):
    if op_token.is_type(parse.OP_EQ):
        return 0B00001000
    elif op_token.is_type(parse.OP_LT):
        return 0B00001001
    elif op_token.is_type(parse.OP_LE):
        return 0B00001010
    elif op_token.is_type(parse.OP_NE):
        return 0B00001011
    elif op_token.is_type(parse.OP_ADD):
        return 0B00100000
    elif op_token.is_type(parse.OP_AND):
        return 0B00100100
    elif op_token.is_type(parse.OP_OR):
        return 0B00100101
    elif op_token.is_type(parse.OP_XOR):
        return 0B00100110
    elif op_token.is_type(parse.OP_SUB):
        return 0B00101000
    elif op_token.is_type(parse.OP_NAND):
        return 0B00101100
    elif op_token.is_type(parse.OP_NOR):
        return 0B00101101
    elif op_token.is_type(parse.OP_NXOR):
        return 0B00101110
    else:
        raise Exception('Unrecognized secondary opcode')


def first_pass(tokens):
    current_index = 0

    for token in tokens:
        if token.is_type(parse.LABEL_DEF):
            labels[token.value] = current_index - 1
        elif token.is_type(parse.DIR_NAME):
            names[token.tokens[0].value] = token.tokens[1].value
        elif token.is_type(parse.DIR_ORIG):
            current_index = token.value
        else:
            current_index += 1


def second_pass(tokens):
    instructions = []

    for token in tokens:
        if token.is_type(parse.DIR_ORIG):
            if token.value < len(instructions):
                raise Exception('ORIG backtracking!')

            for i in range(token.value - len(instructions)):
                instructions.append(0xDEADDEAD)
        elif token.is_type(parse.DIR_WORD):
            if not labels.get(token.value):
                raise Exception('Identifier \'{0}\' not found'.format(token.value))

            instructions.append(labels.get(token.value))
        elif token.is_type(parse.INST):
            inst = 0
            op_token = token.tokens[0]

            if token.is_type(parse.INST_FUNCR):
                secondary_opcode = get_secondary_opcode(token.tokens[0])
                regno_d = token.tokens[1].value
                regno_s = token.tokens[2].value
                regno_t = token.tokens[3].value
                inst = 0 | (regno_s << 20) | (regno_t << 14) | (regno_d << 8) | secondary_opcode
            else:
                primary_opcode = get_primary_opcode(op_token)

                if token.is_type(parse.INST_JUMP) or token.is_type(parse.INST_STORE) or token.is_type(parse.INST_LOAD):
                    regno_t = token.tokens[1].value
                    regno_s = token.tokens[2].tokens[1].value
                    imm_token = token.tokens[2].tokens[0]
                elif token.is_type(parse.INST_BRANCH) or token.is_type(parse.INST_FUNCI):
                    regno_t = token.tokens[1].value
                    regno_s = token.tokens[2].value
                    imm_token = token.tokens[3]
                else:
                    raise Exception('Unrecognized instruction type')

                if imm_token.is_type(parse.IDENTIFIER):
                    if labels.get(imm_token.value):
                        imm = labels.get(imm_token.value) - len(instructions)
                    elif names.get(imm_token.value):
                        imm = names.get(imm_token.value)
                    else:
                        raise Exception('Identifier \'{0}\' not found'.format(imm_token.value))
                else:
                    imm = imm_token.value

                inst = 0 | (primary_opcode << 26) | (regno_s << 20) | (regno_t << 14) | (imm & 0B00000000000000000011111111111111)

            instructions.append(inst)

    return instructions


def create_groups(values):
    current = values[0]
    groups = [[current]]

    for value in values[1:]:
        if value == current:
            groups[-1].append(value)
        else:
            current = value
            groups.append([value])

    return groups


def hex_str(num):
    h = '{0:x}'.format(num)

    for i in range(8 - len(h)):
        h = '0' + h

    return h


def generate(tokens):
    first_pass(tokens)
    instructions = second_pass(tokens)
    groups = create_groups(instructions)
    current = 0

    print('WIDTH=32;')
    print('DEPTH=16384;')
    print('ADDRESS_RADIX=HEX;')
    print('DATA_RADIX=HEX;')
    print('CONTENT BEGIN')

    for group in groups:
        if len(group) == 1:
            print('{0} : {1};'.format(hex_str(current), hex_str(group[0])))
        else:
            print('[{0}..{1}] : {2};'.format(hex_str(current), hex_str(current + len(group)), hex_str(group[0])))

        current += len(group)

    print('[{0}..{1}] : deaddead;'.format(hex_str(current), hex_str(16384)))
    print('END;')












