import unittest
from morphology import Analyser
from tokeniser import Token


class TestMorphology(unittest.TestCase):

    def setUp(self):
        self.morph = Analyser()

    def test_stemmer(self):

        ana = self.morph.analyse(Token('мама'))
        self.assertEqual(ana, ('мам',))

        ana = self.morph.analyse(Token('мамами'))
        self.assertEqual(ana, ('мам', 'мама', 'мамам'))

        ana = self.morph.analyse(Token('мамань'))
        self.assertEqual(ana, ('маман',))

        ana = self.morph.analyse(Token('абажурите'))
        self.assertEqual(ana, ('абажур', 'абажурит'))

    def test_lemmatiser(self):

        ana = self.morph.analyse(Token('а'))
        self.assertEqual(ana, ('а',))

        ana = self.morph.analyse(Token('абазинцами'))
        self.assertEqual(ana, ('абазинец',))

        ana = self.morph.analyse(Token('абажурчик'))
        self.assertEqual(ana, ('абажурчик',))


if __name__ == '__main__':
    unittest.main()
