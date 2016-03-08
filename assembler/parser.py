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


class Parser(object):
    def __init__(self):
        self.parsers = []
        self.tokens = []


    def parse(self, instruction):
        instruction = instruction.strip()
        instruction = re.split('\S', instruction)

        for i in instruction:
            


    def number(token
