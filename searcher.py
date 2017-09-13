import collections
import shelve
import sys
import time
from tokeniser import tokenise
from indexer import Position
from stemmer import stemmer_by_token


def get_n_sort(query, d, doc, cit_off_lim):
    # Словарь для отслеживания текущего положения в списке позиций токенов
    tracker = dict()
    # Словарь из текущих позиций (минимум выбирается из них) и их токенов - для корректного обновления позиции
    pos_front = dict()
    # Счётчик для учёта оффсета и лимита
    counter = 0
    # Ссылка на каждую предыдущую позицию (чтобы не выдавались одинаковые)
    pre_min_pos = False

    while True:
        # Сначала очищаем словарь текущих позиций
        pos_front.clear()

        for t in tokenise(query):
            for s in stemmer_by_token(t):
                if s in d.keys():

                    if s in tracker.keys():
                        # У одного из токенов позиции могут закончиться раньше, но это *не* повод останавливать цикл:
                        # просто делаем позицию недосягаемой, и сравнение всегда проходит в пользу оставшихся
                        try:
                            pos_front[d[s][doc][tracker[s]]] = s
                        except IndexError:
                            pos_front[Position(sys.maxsize, sys.maxsize, sys.maxsize)] = s
                    else:
                        # Первый проход
                        tracker[s] = 0
                        pos_front[d[s][doc][0]] = s

        # Второй сценарий остановки цикла - достижение лимита. Но поскольку просто игнорировать
        # позиции до оффсета мы не можем (где-то накапливать их всё равно надо), учитываем и его
        counter += 1
        if counter > cit_off_lim[0] + cit_off_lim[1]:
            break
        else:
            # Надо узнать, позицию которого из токенов мы выдаём
            min_pos = min(pos_front.keys(), key=lambda x: (x.line, x.start))
            # Обновляем трекер *здесь*
            tracker[pos_front[min_pos]] += 1

            if counter > cit_off_lim[0]:
                if not pre_min_pos or (pre_min_pos and pre_min_pos != min_pos):
                    pre_min_pos = min_pos
                    yield min_pos


def search(query, db_path, doc_off, doc_lim, cit_off_lim):

    doc_sets = list()
    final_docs = list()
    positions = collections.OrderedDict()

    with shelve.open(db_path) as d:
        # Собираем список множеств документов, содержащих псевдоосновы
        for t in tokenise(query):
            for s in stemmer_by_token(t):
                if s in d.keys():
                    doc_sets += [set(doc for doc in d[s].keys())]
                else:
                    doc_sets += [set()]

        # Исключение на случай, если задан пустой поисковый запрос
        try:
            req_docs = doc_sets[0]
        except IndexError:
            return positions

        # Пересекаем полученные множества и сортируем
        for doc_set in doc_sets:
            req_docs &= doc_set
        req_docs = sorted(req_docs)

        # Оффсет и лимит учитываем исключительно *в рамках полученного пересечения*,
        # а не всей коллекции проиндексированных документов: их перечень нам неизвестен
        for i in range(doc_off, doc_off + doc_lim):
            try:
                final_docs += [req_docs[i]]
            except IndexError:
                break

        # Сценарий, когда подходящих документов не нашлось
        if not final_docs:
            return positions

        # Собираем списки позиций (с учётом оффсета и лимита)
        for i, doc in enumerate(final_docs):
            positions[doc] = list(get_n_sort(query, d, doc, cit_off_lim[i]))

        return positions


def tag(query, db_path, doc_off, doc_lim, cit_off_lim):
    # Попутно отмечаем время, затрачиваемое на поиск
    timestamp = time.time()
    positions = search(query, db_path, doc_off, doc_lim, cit_off_lim)
    print('Search completed in {0:.3} s'.format(time.time() - timestamp))
    concord_by_file = collections.OrderedDict()

    for doc in positions.keys():
        # Здесь храним полученные предложения
        concord = []

        for pos in positions[doc]:
            # Поток одноразовый, поэтому каждый раз приходится открывать файл заново
            f = open(doc, mode='r', encoding='utf-8')

            for i, ln in enumerate(f):
                # Перво-наперво доходим до нужного абзаца
                if i == pos.line:
                    # Задаём границы предложения по умолчанию
                    l_border = 0
                    r_border = len(ln)

                    # Ищем границы сами
                    for j in range(pos.start, 0, -1):
                        if ln[j] in '.?!…':
                            l_border = j
                            break

                    for k in range(pos.end, len(ln)):
                        if ln[k] in '.?!…':
                            r_border = k
                            break

                    # Для левой границы делаем небольшую поправку
                    if l_border != 0:
                        l_border += 2

                    left = ln[l_border:pos.start]
                    word = ln[pos.start:pos.end]
                    right = ln[pos.end:r_border + 1]

                    # Определяем предыдущую цитату (для склеивания)
                    pre_quote = ''
                    if concord:
                        pre_quote = concord[-1].replace('<b>', '').replace('</b>', '')

                    # Либо склеиваем, либо добавляем в искомый массив
                    if left + word + right == pre_quote:
                        tag_count = concord[-1].count('<b>')
                        quote = '%s<b>%s</b>%s' % (concord[-1][: pos.start - l_border + (tag_count * 7)], word, right)
                        concord[-1] = quote
                    else:
                        quote = '%s<b>%s</b>%s' % (left, word, right)
                        concord += [quote]

                    # Дальнейшие абзацы просматривать не нужно
                    break

            f.close()
        concord_by_file[doc] = concord
    return concord_by_file
