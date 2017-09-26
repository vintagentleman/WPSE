import unittest
import stemmer
from tokeniser import Token


class TestStemmer(unittest.TestCase):

    def test_normal(self):
        ana = stemmer.stemmer('мама, мамами, мамань, а')

        self.assertEqual(ana, {
            'мама': [('мам', 'а')],
            'мамами': [('мам', 'ами'), ('мама', 'ми'), ('мамам', 'и')],
            'мамань': [('маман', 'ь')],
            'а': [('а', '')],
        })

        ana = stemmer.stemmer_by_token(Token('мама'))
        self.assertEqual(ana, ('мам',))

        # Теперь здесь одна интерпретация вместо трёх
        ana = stemmer.stemmer_by_token(Token('мамами'))
        self.assertEqual(ana, ('мам',))

        ana = stemmer.stemmer_by_token(Token('мамань'))
        self.assertEqual(ana, ('маман',))

        ana = stemmer.stemmer_by_token(Token('а'))
        self.assertEqual(ana, ('а',))

    def test_greedy(self):
        ana = stemmer.greedy_stemmer('папа, папами, папань, и')

        self.assertEqual(ana, {
            'папа': 'пап',
            'папами': 'пап',
            'папань': 'папан',
            'и': 'и',
        })

        ana = stemmer.greedy_stemmer_by_token(Token('папа'))
        self.assertEqual(ana, 'пап')

        ana = stemmer.greedy_stemmer_by_token(Token('папами'))
        self.assertEqual(ana, 'пап')

        ana = stemmer.greedy_stemmer_by_token(Token('папань'))
        self.assertEqual(ana, 'папан')

        ana = stemmer.greedy_stemmer_by_token(Token('и'))
        self.assertEqual(ana, 'и')

    def test_empty(self):
        self.assertEqual(stemmer.stemmer(''), {})
        self.assertEqual(stemmer.greedy_stemmer(''), {})

        # Таких токенов просто быть не может
        # self.assertEqual(stemmer.stemmer_by_token(Token('')), ('',))
        # self.assertEqual(stemmer.greedy_stemmer_by_token(Token('')), '')


if __name__ == '__main__':
    unittest.main()
