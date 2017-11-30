import unittest
import chunker


class TestChunker(unittest.TestCase):

    def test_all_morphs_in_dict(self):
        self.assertEqual(list(chunker.chunk(chunker.MORPH, 'мамами')), [
            ['мам', 'а', 'ми'],
            ['мам', 'ам', 'и'],
            ['мам', 'ами'],
        ])

    def test_some_morphs_not_in_dict(self):
        self.assertEqual(list(chunker.chunk(chunker.MORPH, 'маманя')), [
            ['мам', 'а'],
        ])

    def test_init_morph_not_in_dict(self):
        self.assertEqual(list(chunker.chunk(chunker.MORPH + ['е'], 'сумамед')), [
            ['мам', 'е']
        ])


if __name__ == '__main__':
    unittest.main()
