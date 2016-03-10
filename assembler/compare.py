import sys
import re
import parse


m1 = sys.argv[1]
m2 = sys.argv[2]


def get_lines(f):
    return [line.strip() for line in f.readlines() if line.strip()[0] == '[' or re.match('\d', line.strip()[0])]


def split_line(line):
    return [part.strip().strip(';') for part in re.split('\s+:\s+', line)]


def get_hex(value):
    value = '0x' + value.upper()
    return parse.parse_hex_number(value)


def produce_range(line):
    values = []
    split = split_line(line)
    range_values = split[0].strip('[]').split('..')
    range_values = [get_hex(value) for value in range_values]
    value = split[1].upper()

    for i in range(range_values[1] - range_values[0] + 1):
        values.append(value)

    return values


def produce_values(lines):
    values = []

    for line in lines:
        if re.match('^\[\w+\.\.\w+\]\s+:\s+\w+;$', line):
            values = values + produce_range(line)
        else:
            value = split_line(line)[1]
            value = value.upper()
            values.append(value)

    return values


def main():
    with open(m1, 'r') as f:
        m1_lines = get_lines(f)

    with open(m2, 'r') as f:
        m2_lines = get_lines(f)

    m1_values = produce_values(m1_lines)
    m2_values = produce_values(m2_lines)

    for i in range(len(m1_values)):
        if m1_values[i] != m2_values[i]:
            print('conflict at instruction {0}, file 1 had {1} and file 2 had {2}'.format(i, m1_values[i], m2_values[i]))
            return


if __name__ == '__main__':
    main()
