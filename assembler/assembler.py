import sys
import os
import parse
from regex import re_unwrap, re_wrap, re_or, re_combine


try:
    assembly_file = sys.argv[1]
except:
    print('ERROR: you must supply the path to an assembly file')
    sys.exit(1)


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

    tokens = []
    line_num = 1

    with open(assembly_file) as f:
        for line in f:
            try:
                sanitized = sanitize_line(line)

                if sanitized:
                    tokens.append(parse.parse_line(sanitized))
                else:
                    print('skipped line: {0}'.format(line))
            except Exception as e:
                raise Exception('Error at line number {0}: {1}'.format(line_num, str(e)))

            line_num += 1


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print('ERROR: {0}'.format(str(e)))
        sys.exit(1)
