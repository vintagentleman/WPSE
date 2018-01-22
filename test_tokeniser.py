import unittest
from tokeniser import Tokeniser


class TestTokeniser(unittest.TestCase):

    def setUp(self):
        self.t = Tokeniser()

    def test_plain(self):
        self.assertEqual(
            list(token.string for token in self.t.tokenise('Скоро осень, за окнами август, От дождя потемнели кусты...')),
            ['Скоро', 'осень', 'за', 'окнами', 'август', 'От', 'дождя', 'потемнели', 'кусты']
        )

    def test_punctuation(self):
        self.assertEqual(
            list(token.string for token in self.t.tokenise('What the— Dear me… A “public school–educated snob,” d’ya say?!')),
            ['What', 'the', 'Dear', 'me', 'A', 'public', 'school', 'educated', 'snob', 'd', 'ya', 'say']
        )

    def test_digits(self):
        self.assertEqual(
            list(token.string for token in self.t.tokenise('On a scale from 0 to 10.0, I\'m a 9,75-level Harry Potter fan.')),
            ['On', 'a', 'scale', 'from', '0', 'to', '10.0', 'I', 'm', 'a', '9,75', 'level', 'Harry', 'Potter', 'fan']
        )


if __name__ == '__main__':
    unittest.main()
