import re

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


