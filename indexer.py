import shelve
from functools import total_ordering
from tokeniser import Tokeniser
from morphology import Analyser


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


class Indexer(object):

    def __init__(self):
        self.morph = Analyser()

    def index(self, db_path, file_path):
        db = shelve.open(db_path)
        file = open(file_path, mode='r', encoding='utf-8')

        for i, line in enumerate(file):
            for token in Tokeniser.tokenise(line):
                if token.kind in ('ALPHABETIC', 'NUMERIC'):
                    for norm in self.morph.lemmatiser(token):
                        p = Position(i, token.start, token.end)

                        data = db.setdefault(norm, {})
                        data.setdefault(file_path, []).append(p)
                        db[norm] = data

        db.close()
        file.close()


if __name__ == '__main__':
    indexer = Indexer()
    indexer.index('w&p_vol_1-2', 'volume-2.txt')
