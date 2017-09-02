from tokeniser import tokenise


infl_glob = {
    'а', 'и', 'е', 'у', 'ой', 'ам', 'ами', 'ах',
}


def stemmer(s):

    # Словарь: ключи - токены, значения - кортежи из версий разбоов
    d = {}

    # Максимум среди длин флексий в словаре
    max_len = max(len(fl) for fl in infl_glob)

    # Пробегаем по каждому токену
    for token in tokenise(s):
        t = token.string

        # Выделяем множество его конечных подстрок длины, не превосходящей max_len
        infl_opts = set(t[-i:] for i in range(max_len + 1))

        # Пересекаем его со словарём флексий
        infl = infl_glob & infl_opts

        if infl:
            for fl in infl:
                d.setdefault(t, []).append((t[:-len(fl)], fl))
        else:
            d.setdefault(t, []).append((t, ''))

    return d
