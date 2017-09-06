import unittest
import stemmer


class TestStemmer(unittest.TestCase):

    def test_normal(self):
        ana = stemmer.stemmer('мама, мамами, мамань, а')

        self.assertEqual(ana, {
            'мама': [('мам', 'а')],
            'мамами': [('мамам', 'и'), ('мам', 'ами')],
            'мамань': [('мамань', '')],
            'а': [('', 'а')],
        })

    def test_greedy(self):
        ana = stemmer.greedy_stemmer('папа, папами, папань, и')

        self.assertEqual(ana, {
            'папа': 'пап',
            'папами': 'пап',
            'папань': 'папань',
            'и': '',
        })


if __name__ == '__main__':
    unittest.main()
