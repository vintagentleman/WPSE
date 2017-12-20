import unittest
import chunker


class TestChunker(unittest.TestCase):

    def setUp(self):
        self.chunker = chunker.Chunker()

    def test_all_morphs_in_dict(self):
        self.assertEqual(list(self.chunker.chunk('ами')), [
            {'а': 'pr', 'ми': 'r_Nn', '': 'f_Nn'},
        ])

        self.assertEqual(list(self.chunker.chunk('мама')), [
            {'мам': 'r_Nn', 'а': 'f_Nn'},
        ])

        self.assertEqual(list(self.chunker.chunk('мамами')), [
            {'мам': 'r_Nn', 'ами': 'f_Nn'}
        ])

    def test_partial_segmentation(self):
        self.assertEqual(list(self.chunker.chunk('маманя')), [
            {'мам': 'r_Nn', 'а': 'f_Nn'}
        ])

        self.assertEqual(list(self.chunker.chunk('сумамед')), [
            {'мам': 'r_Nn', 'е': 'f_Nn'}
        ])

    def test_full_segmantation(self):
        self.assertEqual(list(self.chunker.chunk('мама', full=True)), [
            {'мам': 'r_Nn', 'а': 'f_Nn'},
        ])

        self.assertEqual(list(self.chunker.chunk('по-мамски', full=True)), [
            {'по': 'pr', 'мам': 'r_Nn', 'ск': 's_Dr_Aj', 'и': 's_Dr_Av'}
        ])

        self.assertEqual(list(self.chunker.chunk('смотреть', full=True)), [
            {'смотр': 'r_Vb', 'е': 's_Dr_Vb', 'ть': 'f_Vb'}
        ])

        self.assertEqual(list(self.chunker.chunk('понасмотревшийся', full=True)), [
            {'по': 'pr', 'на': 'pr', 'смотр': 'r_Vb', 'е': 's_Dr_Vb', 'вш': 's_Fl_Vb', 'ий': 'f_Aj', 'ся': 'ps'},
        ])

        self.assertEqual(list(self.chunker.chunk('сумамед', full=True)), [])


if __name__ == '__main__':
    unittest.main()
