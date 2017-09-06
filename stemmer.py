from tokeniser import tokenise


infl_glob = {
    # Окончания второго склонения
    'а', 'и', 'е', 'у', 'ой', 'ою', 'ам', 'ами', 'ах',
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

            # Выделяем множество его конечных подстрок длины, не превосходящей max_len
            infl_opts = set(t[-i:] for i in range(max_len + 1))

            # Пересекаем его со словарём флексий и сортируем по возрастанию длины
            infl = sorted(infl_glob & infl_opts, key=lambda x: len(x))

            if infl:
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

            infl_opts = set(t[-i:] for i in range(max_len + 1))
            infl = sorted(infl_glob & infl_opts, key=lambda x: len(x))

            if infl:
                d[t] = t[:-len(infl[-1])]
            else:
                d[t] = t

    return d
