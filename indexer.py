import shelve
from tokeniser import tokenise


class Position(object):

    def __init__(self, line, start, end):
        self.line = line
        self.start = start
        self.end = end


def index(file_path, db_path):

    with shelve.open(db_path) as d:
        with open(file_path, mode='r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                for token in tokenise(line):
                    if token.kind in ('ALPHABETIC', 'NUMERIC'):
                        p = Position(i, token.start, token.end)

                        data = d.setdefault(token.string, {})
                        data.setdefault(file_path, []).append(p)
                        d[token.string] = data
