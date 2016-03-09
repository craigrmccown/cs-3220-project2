import sys
import os
import parse
import generate


try:
    assembly_file = sys.argv[1]
except:
    print('ERROR: you must supply the path to an assembly file')
    sys.exit(1)


def sanitize_line(line):
    if ';' in line:
        line = line.split(';')[0]

    line = line.strip()

    if line == '':
        return None

    return line


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
                    tokens.append(parse.parse_line(sanitized, line_num))
            except parse.ParseException as e:
                raise parse.ParseException('Error at line number {0}: {1}, {2}'.format(line_num, line.strip(), str(e)))

            line_num += 1

    generate.generate(tokens)


if __name__ == '__main__':
    try:
        main()
    except parse.ParseException as e:
        print('Error: {0}'.format(str(e)))
    except generate.UndefinedSymbolException as e:
        line_num = e.token.attributes.get('line_num')
        text = e.token.attributes.get('text')
        print('Undefined error at line {0}: {1}'.format(line_num, text))
        print(str(e))
    except generate.SemanticException as e:
        line_num = e.token.attributes.get('line_num')
        text = e.token.attributes.get('text')
        print('Semantic error at line {0}: {1}'.format(line_num, text))
        print(str(e))
