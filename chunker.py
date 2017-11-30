from string_algorithms import aho_corrasick
from tokeniser import Token


MORPH = [
    'а',
    'ам',
    'ами',
    'и',
    'мам',
    'ми',
]


def morph_gener(d, pos=0, chain=[]):
    if pos in d:
        # Начинаем либо продолжаем обход словаря
        morph_list = d[pos]

    # Поиск может не получиться в двух случаях: в начале и в конце
    else:
        # Либо словоформа может начинаться не с 1-го сегмента, выделенного Ахо - Корасик
        # В таком случае берём сегмент, ближе всего отстоящий от начала
        if pos == 0:
            morph_list = d[min(d)]
        # Либо мы дошли до последнего сегмента, с конечной позиции которого ничто не начинается
        # Тогда выдаём всю накопленную цепочку и заканчиваем обход данной ветки
        else:
            yield chain
            return

    for morph in morph_list:
        yield from morph_gener(d, morph.end, chain + [morph.string])


def chunk(morph_dict, string):
    # Словарь вида {0: ['м', 'мам'], 3: ['а', 'ам', 'ами']}
    d = {}

    for pair in aho_corrasick.find(morph_dict, string):
        morph = Token(pair[1], pair[0])
        d.setdefault(morph.start, []).append(morph)

    return morph_gener(d)
