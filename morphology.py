import shelve
# from tokeniser import tokenise


infl_glob = {
    # Источник: http://www.slovorod.ru/russian-inflexions.html
    'а',   'ал',  'ала', 'али', 'ам',  'ами', 'ас',  'ать', 'ах',  'ая',
    'е',   'его', 'ее',  'её',  'ей',  'ем',  'еми', 'емя', 'ет',  'ете', 'еть', 'ех', 'ешь', 'ею',
    'ёт',  'ёте', 'ёх',  'ёшь',
    'и',   'ие',  'ий',  'им',  'ими', 'ит',  'ите', 'их',  'ишь', 'ию',
    'м',   'ми',  'мя',
    'о',   'ов',  'ого', 'ое',  'ой',  'ом',  'ому', 'ою',  'оё',
    'см',
    'у',   'ул',  'ула', 'ули', 'ум',  'умя', 'ут',  'уть', 'ух',  'ую',
    'шь',
    'ы',   'ый',
    'ь',
    'ю',   'ют',
    'я',   'ял',  'яла', 'яли', 'ять', 'яя',
}


def analyser(t, wikidata='rus_nom'):
    d = shelve.open(wikidata)
    s = t.string

    otpt_s = []
    otpt_i = None

    max_len = max(len(x) for x in d if any(d[x][i] is None for i in d[x]))

    # Лемматизация
    for i in range(max_len, -1, -1):
        if i != 0:
            stem = s[:-i]
            infl = s[-i:]
        else:
            stem = s
            infl = ''

        # Условие 1: основа непустая и есть в базе
        if stem and stem in d:
            # Условие 2: флексия есть в базе и является флексией
            if infl in d.keys() and any(x is None for x in d[infl].values()):
                common = set(d[stem]) & set(d[infl])

                # Условие 3: есть общие пары вида ('шаблон', 'тип основы')
                if common:
                    for pair in common:
                        lemma = d[stem][pair]
                        if lemma:
                            otpt_s.append(lemma)

    # Стемминг:
    # выделяем множество конечных подстрок длины, не превосходящей максимальную;
    # затем пересекаем его со словарём флексий и сортируем по возрастанию длины
    if not otpt_s:
        otpt_i = sorted(set(s[-i:] for i in range(max_len, 0, -1) if s[-i:] in infl_glob), key=lambda x: -len(x))

    if otpt_s:
        return tuple(sorted(otpt_s))

    elif otpt_i is not None:
        # Случай, когда основа совпала с флексией
        if len(otpt_i) == 1 and otpt_i[0] == s:
            return s,
        else:
            return tuple(s[:-len(fl)] for fl in otpt_i)

    else:
        return s,
