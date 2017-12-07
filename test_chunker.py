import unittest
import chunker


class TestChunker(unittest.TestCase):

    def setUp(self):
        self.md = chunker.MD.copy()

    def test_all_morphs_in_dict(self):
        self.assertEqual(list(chunker.chunk(self.md, 'ами')), [
            {'а': 'pr', 'ми': 'r', '': 'f'},
            {'а': 'r', 'ми': 'f'}
        ])

        self.assertEqual(list(chunker.chunk(self.md, 'мамами')), [
            {'мам': 'r', 'а': 's', 'ми': 'f'},
            {'мам': 'r', 'ами': 'f'}
        ])

    def test_some_morphs_not_in_dict(self):
        self.assertEqual(list(chunker.chunk(self.md, 'маманя')), [
            {'мам': 'r', 'а': 's', '': 'f'},
            {'мам': 'r', 'а': 'f'}
        ])

    def test_init_morph_not_in_dict(self):
        self.md.update({'е': ['i', 's', 'f']})

        self.assertEqual(list(chunker.chunk(self.md, 'сумамед')), [
            {'мам': 'r', 'е': 's', '': 'f'},
            {'мам': 'r', 'е': 'f'}
        ])


if __name__ == '__main__':
    unittest.main()
