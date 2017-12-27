import re
from string import punctuation


class Token(object):

    def __init__(self, string, column=0, kind='ALPHABETIC'):
        self.string = string
        self.length = len(string)
        self.start = column
        self.end = column + self.length
        self.kind = kind
    
    def __repr__(self):
        return '(%s) \'%s\' [%d..%d]' % (self.kind, self.string, self.start, self.end)


class Tokeniser(object):

    @staticmethod
    def tokenise(s):

        token_specs = [
            ('ALPHABETIC', r'\w+'),
            ('NUMERIC', r'\d+([.,]\d*)?'),
            ('PUNCTUATION', r'[%s]+' % punctuation),
            ('WHITESPACE', r'[\n \t]+'),
            ('UNKNOWN', r'.'),
        ]

        token_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specs)

        for match in re.finditer(token_regex, s):
            kind = match.lastgroup
            string = match.group(kind)

            if kind in ('ALPHABETIC', 'NUMERIC'):
                yield Token(string, match.start(), kind)
