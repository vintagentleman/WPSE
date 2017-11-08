import shelve
from functools import total_ordering
from tokeniser import tokenise
from morphology import analyser


@total_ordering
class Position(object):

    def __init__(self, line, start, end):
        self.line = line
        self.start = start
        self.end = end

    def __repr__(self):
        return 'line %s | column %s-%s' % (self.line, self.start, self.end)

    # Для возможности хранить объекты как ключи словаря
    def __hash__(self):
        return hash((self.line, self.start))

    def __eq__(self, other):
        return (self.line, self.start) == (other.line, other.start)

    def __lt__(self, other):
        return (self.line, self.start) < (other.line, other.start)


def index_analysed_tokens(file_path, db_path):

    with shelve.open(db_path) as d:
        with open(file_path, mode='r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                for token in tokenise(line):
                    if token.kind in ('ALPHABETIC', 'NUMERIC'):
                        for norm in analyser(token):
                            p = Position(i, token.start, token.end)

                            data = d.setdefault(norm, {})
                            data.setdefault(file_path, []).append(p)
                            d[norm] = data


if __name__ == '__main__':
    index_analysed_tokens('sample-3.txt', 'sample-test')
