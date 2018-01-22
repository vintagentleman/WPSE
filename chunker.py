import re
from itertools import product
from collections import defaultdict
from string_algorithms import aho_corrasick
from tokeniser import Token


class FSM(object):

    network = {
        'START': {'pr', 'r_Nn', 'r_Aj', 'r_Vb', 'r_Zz'},
        'pr': {'pr', 'r_Nn', 'r_Aj', 'r_Vb', 'r_Zz'},

        'r_Nn': {'i', 's_Dr_Nn', 's_Fl_Nn', 's_Dr_Aj', 'f_Nn', 'END'},
        'r_Aj': {'i', 's_Dr_Aj', 's_Fl_Aj', 's_Dr_Av', 'f_Aj', 'END'},
        'r_Vb': {'i', 's_Dr_Vb', 's_Fl_Vb', 'f_Vb', 'END'},
        'r_Zz': {'END'},

        'i': {'pr', 'r_Nn', 'r_Aj', 'r_Vb', 'r_Zz'},

        's_Dr_Nn': {'s_Dr_Nn', 's_Fl_Nn', 'f_Nn', 'END'},
        's_Dr_Aj': {'s_Dr_Aj', 's_Fl_Aj', 's_Dr_Av', 'f_Aj', 'END'},
        's_Dr_Vb': {'s_Dr_Vb', 's_Fl_Vb', 'f_Vb', 'f_Aj', 'END'},
        's_Dr_Av': {'s_Dr_Av', 'END'},

        's_Fl_Nn': {'s_Fl_Nn', 'f_Nn', 'END'},
        's_Fl_Aj': {'s_Fl_Aj', 'f_Aj', 'END'},
        's_Fl_Vb': {'s_Fl_Vb', 'f_Vb', 'f_Aj', 'END'},

        'f_Nn': {'END'},
        'f_Aj': {'ps', 'END'},
        'f_Vb': {'ps', 'END'},

        'ps': {'END'},
    }

    marked_arcs = {
        ('r_Nn', 'END'): ('', 'f_Nn'),
        ('s_Dr_Nn', 'END'): ('', 'f_Nn'),
        ('s_Fl_Nn', 'END'): ('', 'f_Nn'),

        ('r_Aj', 'END'): ('', 'f_Aj'),
        ('s_Dr_Aj', 'END'): ('', 'f_Aj'),
        ('s_Fl_Aj', 'END'): ('', 'f_Aj'),

        ('r_Vb', 'END'): ('', 's_Fl_Vb'),
        ('s_Dr_Vb', 'END'): ('', 's_Fl_Vb'),
        ('s_Fl_Vb', 'END'): ('', 'f_Vb'),
    }

    def __init__(self):
        self.state = 'START'
        self.mark = None

    def run(self, typ):
        arc = (self.state, typ)

        # На каждом шаге обновляем текущее состояние
        if typ in self.network[self.state]:
            self.state = typ
        else:
            raise RuntimeError('No transition between %s and %s.' % arc)

        # Метки размеченных дуг фиксируем
        self.mark = self.marked_arcs.get(arc)


class Chunker(object):

    def __init__(self):
        self.fsm = FSM()

        self.md = {
            'а': ['pr', 'r_Zz', 's_Dr_Vb', 's_Dr_Av', 'f_Nn', 'f_Vb'],
            'ам': ['f_Nn'],
            'ами': ['f_Nn'],
            'вш': ['r_Nn', 's_Fl_Vb'],
            'е': ['i', 's_Dr_Vb', 'f_Nn'],
            'и': ['r_Zz', 'i', 's_Dr_Vb', 's_Dr_Av', 'f_Nn', 'f_Vb'],
            'ий': ['f_Aj'],
            'мам': ['r_Nn'],
            'ми': ['r_Nn', 'f_Nn'],
            'на': ['pr', 'r_Zz'],
            'по': ['pr', 'r_Zz'],
            'ск': ['s_Dr_Aj', 's_Dr_Av'],
            'смотр': ['r_Nn', 'r_Vb'],
            'ся': ['ps'],
            'ть': ['f_Vb'],
        }

    def chunk(self, s, full=False):
        """
        Порождает сегментации анализируемой словоформы на морфемы на основе конечного автомата.
        Список морфем прописан вручную в атрибуте md. Конечный автомат проверяет сочетаемость их типов.

        :param s: строковое представление токена, подлежащего сегментации
        :param full: режим (необходимо или нет полное покрытие словоформы сегментацией)
        :return: генератор словарей вида {морфема: тип (единственный)}
        """

        d = defaultdict(list)
        s = re.sub('[^\w]', '', s)

        for pair in aho_corrasick.find(self.md, s):
            morph = Token(pair[1], column=pair[0], kind=self.md[pair[1]])
            d[morph.start].append(morph)

        # Генератор возвращает списки возможных сегментаций
        for morph_list in morph_gener(d, len(s), full, 0, []):
            # Для каждой сегментации строим декартово произведение типов её сегментов
            for typ_tup in product(*(self.md[m] for m in morph_list)):
                type_list = list(typ_tup)
                self.fsm.state = 'START'

                try:
                    for i, typ in enumerate(list(typ_tup) + ['END']):
                        self.fsm.run(typ)

                        # Проверяем, не размечена ли пройденная дуга
                        if self.fsm.mark is not None:
                            morph_list.insert(i, self.fsm.mark[0])
                            type_list.insert(i, self.fsm.mark[1])
                except RuntimeError:
                    continue
                else:
                    yield dict(zip(morph_list, type_list))


def morph_gener(d, l, full, pos, chain):
    """
    Строит сегментации на основе списка морфем, выделенных алгоритмом Ахо - Корасик.
    Фактически возвращает пути по связным компонентам графа, построенного на множестве морфем.

    :param d: словарь вида {0: ['м', 'мам'], 3: ['а', 'ам', 'ами'], ...}
    :param l: длина разбираемой словоформы
    :param full: режим (наследуется из метода chunk)
    :param pos: индекс текущей морфемы
    :param chain: накопленная цепочка морфем
    :return: генератор успешно построенных сегментаций
    """

    if pos in d:
        # Начинаем либо продолжаем обход словаря
        morph_list = d[pos]

    # Поиск может не получиться в двух случаях: в начале и в конце
    else:
        # Либо словоформа может начинаться не с 1-го сегмента, выделенного Ахо - Корасик
        # В таком случае берём сегмент, ближе всего отстоящий от начала
        if pos == 0:
            if full:
                return
            else:
                morph_list = d[min(d)]
        # Либо мы дошли до последнего сегмента, с конечной позиции которого ничто не начинается
        # Тогда выдаём всю накопленную цепочку и заканчиваем обход данной ветки
        else:
            if (full and pos == l) or not full:
                yield chain
            return

    for morph in morph_list:
        yield from morph_gener(d, l, full, morph.end, chain + [morph.string])
