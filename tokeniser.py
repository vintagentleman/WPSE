import re


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
        """
        Осуществляет токенизацию - вычленяет из строки алфавитные и цифровые символьные цепочки.
        На основе регулярных выражений, т. к. исходный вариант токенизатора (на основе последовательного применения
        методов isalpha(), isnumeric() и т. д.) был утерян, а на этапе восстановления был сочтён чересчур примитивным.

        :param s: строка, подлежащая разбиению на токены
        :return: генератор, порождающий извлечённые токены
        """

        token_specs = [
            ('NUMERIC', r'\d+([.,]\d*)?'),
            ('ALPHABETIC', r'\w+'),
            ('PUNCTUATION', r'[^\w\s]+'),
            ('WHITESPACE', r'[\s]+'),
            ('UNKNOWN', r'.+'),
        ]

        token_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specs)

        for match in re.finditer(token_regex, s):
            kind = match.lastgroup
            string = match.group(kind)

            if kind in ('ALPHABETIC', 'NUMERIC'):
                yield Token(string, match.start(), kind)
