import re
import shelve
from mwclient import Site


def scrape(database, limit, category):

    def remove_accent(s):

        for c in 'ЀЍѐѝ́̀':
            s = s.replace(c, '')

        return s

    site = Site(('https', 'ru.wiktionary.org'))
    db = shelve.open(database)
    count = 0

    for page in site.categories[category]:
        # Разбиваем викитекст на строки
        lines = page.text().split(sep='\n')

        # Ищем начало искомого раздела
        try:
            # Добавляем единицу, чтобы не приписывать всякий раз
            i = lines.index('=== Морфологические и синтаксические свойства ===') + 1
        except ValueError:
            i = -1

        if i != -1:
            for j, line in enumerate(lines[i:]):
                # Ищем, где начинается шаблон
                if line.startswith('{{') and not line.endswith('}}'):
                    # Фигурные скобки и лишние пробелы (случается) убираем
                    template = line[2:].strip()
                    # Ищём конец текущего шаблона
                    end = lines[i + j + 1:].index('}}')

                    for item in lines[i + j + 1:i + j + end]:
                        if item[1:].startswith('основа'):
                            # В основах избавляемся от лишних же пробелов и ударений
                            name = item[item.index('основа'):item.index('=')].strip()
                            stem = remove_accent(item[item.index('=') + 1:]).strip()
                            if stem:
                                print(stem, template, name)

                                # Типов бывает несколько
                                data = db.setdefault(stem, [])
                                data.append((template, name))
                                db[stem] = data

                # Конец раздела
                elif line.startswith('='):
                    break

        count += 1
        if count > limit:
            break

    for stem in db.keys():
        for pair in db[stem]:
            page = site.pages['Шаблон:' + pair[0]]
            lines = page.text().split(sep='\n')

            for line in lines:
                if 'основа' in line:
                    sub = line[line.index('основа'):]
                    name = re.search('основа\d*(?=[|}])', sub).group()
                    infl = remove_accent(sub[sub.rindex('}') + 1:]).strip()

                    # print(infl, pair[0], name)

                    data = db.setdefault(infl, [])
                    data.append((pair[0], name))
                    db[infl] = data

    db.close()


if __name__ == '__main__':
    scrape('rus_nom', 100, 'Русские_существительные')
