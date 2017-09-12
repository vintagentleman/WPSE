import collections
import os
import unittest
from indexer import index_stems_as_keys
from searcher import tag


class TestSearch(unittest.TestCase):

    def setUp(self):

        with open('test-1.txt', mode='w', encoding='utf-8') as f:
            f.write('''
Тест на слова-флексии: а и о.
Тест на нулевые флексии: пойман волочен повешен четвертован.
Тест на неоднозначность интерпретаций #1: мама мамам мамами.
''')

        with open('test-2.txt', mode='w', encoding='utf-8') as f:
            f.write('''
Тест на слова-флексии: и о у.
Тест на множественность форм одного слова: Наташа Наташи Наташе Наташу.
Тест на неоднозначность интерпретаций #2: папами папам папа.
''')

        for i in (1, 2):
            index_stems_as_keys('test-%d.txt' % i, 'test')

    def tearDown(self):

        for i in (1, 2):
            os.remove('test-%d.txt' % i)

        for extension in ('.bak', '.dat', '.dir'):
            os.remove('test' + extension)

    def test_empty(self):
        query = ''

        self.assertEqual(tag(query, 'test', 0, 2, [(0, 9), (0, 9)]), collections.OrderedDict())

    def test_infl(self):
        query = 'и о'

        self.assertEqual(tag(query, 'test', 0, 2, [(0, 9), (0, 9)]), collections.OrderedDict([
            ('test-1.txt', ['Тест на слова-флексии: а <b>и</b> <b>о</b>.']),
            ('test-2.txt', ['Тест на слова-флексии: <b>и</b> <b>о</b> у.']),
        ]))

    def test_zero(self):
        query = 'пойман повешен'

        self.assertEqual(tag(query, 'test', 0, 2, [(0, 9), (0, 9)]), collections.OrderedDict([
            ('test-1.txt', ['Тест на нулевые флексии: <b>пойман</b> волочен <b>повешен</b> четвертован.']),
        ]))

    def test_plur(self):
        query = 'Наташа'

        self.assertEqual(tag(query, 'test', 0, 2, [(0, 9), (0, 9)]), collections.OrderedDict([
            ('test-2.txt',
             ['Тест на множественность форм одного слова: <b>Наташа</b> <b>Наташи</b> <b>Наташе</b> <b>Наташу</b>.']),
        ]))

    def test_ambig_1(self):
        query = 'мамами'

        self.assertEqual(tag(query, 'test', 0, 2, [(0, 9), (0, 9)]), collections.OrderedDict([
            ('test-1.txt', ['Тест на неоднозначность интерпретаций #1: <b>мама</b> <b>мамам</b> <b>мамами</b>.']),
        ]))

    def test_ambig_2(self):
        query = 'папами'

        self.assertEqual(tag(query, 'test', 0, 2, [(0, 9), (0, 9)]), collections.OrderedDict([
            ('test-2.txt', ['Тест на неоднозначность интерпретаций #2: <b>папами</b> <b>папам</b> <b>папа</b>.']),
        ]))


if __name__ == '__main__':
    unittest.main()
