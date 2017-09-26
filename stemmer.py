from tokeniser import tokenise


infl_glob = {
    # Источник: http://www.slovorod.ru/russian-inflexions.html
    'а', 'ал', 'ала', 'али', 'ам', 'ами', 'ас', 'ать', 'ах', 'ая',
    'е', 'его', 'ее', 'ей', 'ем', 'еми', 'емя', 'ет', 'ете', 'еть', 'ех', 'ешь' 'ею', 'её',
    'ёт', 'ёте', 'ёх', 'ёшь',
    'и', 'ие', 'ий', 'им', 'ими', 'ит', 'ите', 'их', 'ишь', 'ию',
    'м', 'ми', 'мя',
    'о', 'ов', 'ого', 'ое', 'ой', 'ом', 'ому', 'ою', 'оё',
    'см',
    'у', 'ул', 'ула', 'ули', 'ум', 'умя', 'ут', 'уть', 'ух', 'ую',
    'шь',
    'ы', 'ый',
    'ь',
    'ю', 'ют',
    'я', 'ял', 'яла', 'яли', 'ять', 'яя',
}


stem_glob = {
    'мам', 'мы', 'рам',
}


def stemmer(s):

    # Словарь: ключи - токены, значения - кортежи из версий разбоов
    d = {}

    # Максимум среди длин флексий в словаре
    max_len = max(len(fl) for fl in infl_glob)

    # Пробегаем по каждому алфавитному токену
    for token in tokenise(s):
        if token.kind == 'ALPHABETIC':
            t = token.string

            # Выделяем множество его конечных подстрок длины, не превосходящей max_len;
            # затем пересекаем его со словарём флексий и сортируем по возрастанию длины
            infl = sorted(set(t[-i:] for i in range(max_len + 1) if t[-i:] in infl_glob), key=lambda x: -len(x))

            if infl:
                # Особо учитываем случай, когда основа совпала с флексией
                if len(infl) == 1 and infl[0] == t:
                    d.setdefault(t, []).append((t, ''))
                else:
                    for fl in infl:
                        d.setdefault(t, []).append((t[:-len(fl)], fl))
            else:
                d.setdefault(t, []).append((t, ''))

    return d


def greedy_stemmer(s):

    d = {}
    max_len = max(len(fl) for fl in infl_glob)

    for token in tokenise(s):
        if token.kind == 'ALPHABETIC':
            t = token.string
            infl = ''

            # Здесь перебирать всё не нужно, берём только флексию наибольшей длины
            for i in range(max_len, 0, -1):
                if t[-i:] in infl_glob:
                    infl = t[-i:]
                    break

            if infl:
                if infl == t:
                    d[t] = t
                else:
                    d[t] = t[:-len(infl)]
            else:
                d[t] = t

    return d


def stemmer_by_token(t):

    max_len = max(len(fl) for fl in infl_glob)
    s = t.string
    infl = sorted(set(s[-i:] for i in range(max_len + 1) if s[-i:] in infl_glob), key=lambda x: -len(x))

    if infl:
        # Умный стемминг (с привлечением словаря)
        stem = set(s[:-len(fl)] for fl in infl) & stem_glob

        if stem:
            return tuple(stem)
        elif len(infl) == 1 and infl[0] == s:
            return s,
        else:
            return tuple(s[:-len(fl)] for fl in infl)
    else:
        return s,


def greedy_stemmer_by_token(t):

    max_len = max(len(fl) for fl in infl_glob)
    s = t.string
    infl = ''

    for i in range(max_len, 0, -1):
        if s[-i:] in infl_glob:
            infl = s[-i:]
            break

    if infl:
        if infl == s:
            return s
        else:
            return s[:-len(infl)]
    else:
        return s