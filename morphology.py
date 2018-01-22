import shelve
from chunker import Chunker


class Analyser(object):

    def __init__(self, wikidata='ru_noun'):
        self.d = shelve.open(wikidata)

        self.infl_glob = {
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

        # Максимальная длина флексии вычисляется единожды!
        self.max_len = max(len(x) for x in self.d if any(self.d[x][i] is None for i in self.d[x]))
        self.chunker = Chunker()

    def __del__(self):
        self.d.close()

    def lemmatiser(self, t):
        """
        Осуществляет лемматизацию на основе базы морфологических сведений, извлечённых из Викисловаря.
        Если лемматизация не проходит (на основе одного из условий, см. ниже), то делается фолбэк к стеммингу.

        :param t: анализируемый токен
        :return: кортеж из его лемм
        """

        s = t.string
        otpt = []

        for i in range(self.max_len, -1, -1):
            if i != 0:
                stem = s[:-i]
                infl = s[-i:]
            else:
                stem = s
                infl = ''

            # Условие 1: основа непустая и есть в базе
            if stem and stem in self.d:
                # Условие 2: флексия есть в базе и является флексией
                if infl in self.d.keys() and any(x is None for x in self.d[infl].values()):
                    common = set(self.d[stem]) & set(self.d[infl])

                    # Условие 3: есть общие пары вида ('шаблон', 'тип основы')
                    if common:
                        for pair in common:
                            lemma = self.d[stem][pair]
                            if lemma:
                                otpt.append(lemma)

        if otpt:
            return tuple(sorted(otpt))
        else:
            # Фолбэк, если лемматизация не прошла
            return self.stemmer(s)

    def stemmer(self, s):
        """
        Осуществляет стемминг 1) на основе конечного автомата (возможный лишь на ограниченном множестве морфем),
        при неудаче - 2) простым отсечением финали. Последние заданы в атрибуте infl_glob. Если не удаётся
        сделать и это, то просто возвращает строковое представление токена.

        :param s: строковое представление анализируемого токена
        :return: кортеж из его основ
        """

        otpt = set(''.join(m for m in segm if not segm[m].startswith(('f', 's_Fl'))) for segm in self.chunker.chunk(s, full=True))

        if otpt:
            # Стемминг с морфоанализом. Если не прошёл и он - фолбэк к отсечению финали
            return tuple(sorted(otpt))
        else:
            # Выделяем множество конечных подстрок длины, не превосходящей максимальную;
            # затем пересекаем его со словарём флексий и сортируем по возрастанию длины
            infl = sorted(set(s[-i:] for i in range(self.max_len, 0, -1) if s[-i:] in self.infl_glob), key=lambda x: -len(x))

        if infl:
            # Случай, когда основа совпала с флексией
            if len(infl) == 1 and infl[0] == s:
                return s,
            else:
                return tuple(s[:-len(fl)] for fl in infl)

        # Всем фолбэкам фолбэк
        else:
            return s,
