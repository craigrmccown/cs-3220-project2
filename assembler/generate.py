import parse


labels = {}
names = {}


def set_up(tokens):
    for i in range(len(tokens)):
        token = tokens[i]

        if token.is_type(parse.LABEL_DEF):
            labels[token.tokens[0].value] = i
        elif token.is_type(parse.DIR_NAME):
            names[token.tokens[1].value] = token.tokens[2].value

def generate(tokens):
    set_up(tokens)
    print(labels)
    print(names)
