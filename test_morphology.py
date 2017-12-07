import unittest
from morphology import Analyser
from tokeniser import Token


class TestMorphology(unittest.TestCase):

    def setUp(self):
        self.morph = Analyser()

    def stemmer(self):
        ana = self.morph.stemmer('мамами')
        self.assertEqual(ana, ('мам', 'мама'))

    def test_stem_fallback(self):
        ana = self.morph.stemmer('мама')
        self.assertEqual(ana, ('мам',))

        ana = self.morph.stemmer('мамань')
        self.assertEqual(ana, ('маман',))

        ana = self.morph.stemmer('мистическая')
        self.assertEqual(ana, ('мистическ', 'мистическа'))

    def test_lemmatiser(self):
        ana = self.morph.lemmatiser(Token('а'))
        self.assertEqual(ana, ('а',))

        ana = self.morph.lemmatiser(Token('абазинцами'))
        self.assertEqual(ana, ('абазинец',))

        ana = self.morph.lemmatiser(Token('абажурчик'))
        self.assertEqual(ana, ('абажурчик',))

    def test_lem_fallback(self):
        ana = self.morph.lemmatiser(Token('абажурите'))
        self.assertEqual(ana, ('абажур', 'абажурит'))


if __name__ == '__main__':
    unittest.main()
