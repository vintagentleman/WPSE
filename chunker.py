from itertools import product
from string_algorithms import aho_corrasick
from tokeniser import Token


class FSM(object):

    def __init__(self):
        self.state = 'START'

        self.network = {
            'START': ['pr', 'r'],
            'pr': ['pr', 'r'],
            'r': ['i', 's', 'f', 'END'],
            'i': ['pr', 'r'],
            's': ['s', 'f', 'END'],
            'f': ['ps', 'END'],
            'ps': ['END'],
        }

    def run(self, typ_tup):
        # Возвращаемся в начальное состояние
        self.state = 'START'

        for typ in typ_tup:
            if typ in self.network[self.state]:
                # На каждом шаге обновляем текущее состояние
                self.state = typ
            else:
                raise RuntimeError('No transition between %s and %s.' % (self.state, typ))

        # OK, если текущее состояние 1) достигнуто и 2) предтерминальное; в противном случае - исключение
        if 'END' not in self.network[self.state]:
            raise RuntimeError('No transition between %s and END.' % self.state)


class Chunker(object):

    def __init__(self):
        self.fsm = FSM()

        self.md = {
            'а': ['pr', 'r', 's', 'f'],
            'ам': ['f'],
            'ами': ['f'],
            'и': ['r', 'i', 's', 'f'],
            'мам': ['r'],
            'ми': ['r', 'f'],
        }

    def chunk(self, string, full=False):
        # Словарь вида {0: ['м', 'мам'], 3: ['а', 'ам', 'ами']}
        d = {}

        for pair in aho_corrasick.find(self.md, string):
            morph = Token(pair[1], column=pair[0], kind=self.md[pair[1]])
            d.setdefault(morph.start, []).append(morph)

        # Генератор возвращает списки возможных сегментаций
        for morph_list in morph_gener(d, len(string), full):
            # Для каждой сегментации строим декартово произведение типов её сегментов
            for typ_tup in product(*(self.md[m] for m in morph_list)):
                try:
                    self.fsm.run(typ_tup)
                except RuntimeError:
                    continue
                else:
                    # Дополнительно учитываем нулевую флексию
                    if self.fsm.state in ('r', 's'):
                        yield dict(zip(morph_list + [''], list(typ_tup) + ['f']))
                    # Возвращаем словарь вида {морфема: тип (единственный)}
                    else:
                        yield dict(zip(morph_list, list(typ_tup)))


def morph_gener(d, l, full, pos=0, chain=[]):
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
