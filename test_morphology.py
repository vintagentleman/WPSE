import unittest
import morphology
from tokeniser import Token


class TestMorphology(unittest.TestCase):

    def test_stemmer(self):

        ana = morphology.analyser(Token('мама'))
        self.assertEqual(ana, ('мам',))

        ana = morphology.analyser(Token('мамами'))
        self.assertEqual(ana, ('мам', 'мама', 'мамам'))

        ana = morphology.analyser(Token('мамань'))
        self.assertEqual(ana, ('маман',))

        ana = morphology.analyser(Token('абажурите'))
        self.assertEqual(ana, ('абажур', 'абажурит'))

    def test_lemmatiser(self):

        ana = morphology.analyser(Token('а'))
        self.assertEqual(ana, ('а',))

        ana = morphology.analyser(Token('абазинцами'))
        self.assertEqual(ana, ('абазинец',))

        ana = morphology.analyser(Token('абажурчик'))
        self.assertEqual(ana, ('абажурчик',))


if __name__ == '__main__':
    unittest.main()
