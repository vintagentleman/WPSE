import unittest
import server


class TestPager(unittest.TestCase):

    def setUp(self):
        # Кортежи вида (оффсет по цитатам, лимит по цитатам) для каждого документа
        self.cit_off_lim = [(20, 9), (0, 9)]
        # Вновь заданные лимиты по цитатам (строки, ибо в ходе работы извлекаются из формы)
        self.lim_cit = ['10', '10']
        # Оффсет и лимит по документам
        self.offset = 5
        self.limit = 2

    def test_cit_pager(self):
        # Имеем в виду, что список в ходе работы мутирует
        self.assertEqual(server.WPSE.cit_pager(self.cit_off_lim, self.lim_cit, self.limit, 'prev_cit_0'), [(10, 9), (0, 9)])
        self.assertEqual(server.WPSE.cit_pager(self.cit_off_lim, self.lim_cit, self.limit, 'next_cit_1'), [(10, 9), (10, 9)])
        self.assertEqual(server.WPSE.cit_pager(self.cit_off_lim, self.lim_cit, self.limit, 'prev_cit_1'), [(10, 9), (0, 9)])
        self.assertEqual(server.WPSE.cit_pager(self.cit_off_lim, self.lim_cit, self.limit, 'home_cit_0'), [(0, 9), (0, 9)])

    def test_doc_pager(self):
        # С другой стороны, числа немутабельны - новый оффсет просто возвращается
        self.assertEqual(server.WPSE.doc_pager(self.offset, self.limit, 'next_doc'), 7)
        self.assertEqual(server.WPSE.doc_pager(self.offset, self.limit, 'prev_doc'), 3)
        self.assertEqual(server.WPSE.doc_pager(self.offset, self.limit, 'home_doc'), 1)


if __name__ == '__main__':
    unittest.main()
