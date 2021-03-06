import re
import shelve
from mwclient import Site


class Wiktioneer(object):

    def __init__(self, db, limit=5000, category='Русские_существительные'):
        self.site = Site(('https', 'ru.wiktionary.org'))
        self.db = shelve.open(db)
        self.limit = limit
        self.category = category

    def __del__(self):
        self.db.close()

    def scrape(self):
        """
        Создаёт базу морфологических сведений, извлечённых из русскоязычного Викисловаря.
        По умолчанию данные извлекаются из статей категории 'Русские существительные'.
        Количество обрабатываемых статей определяется атрибутом limit (по умолчанию - 5000).

        Структура базы: {
            'основа_1': {
                ('шаблон_x', 'тип_основы_x'): 'лемма_x',
                ('шаблон_y', 'тип_основы_y'): 'лемма_y',
            },
            'основа_2': {
                ('шаблон_z', 'тип_основы_z'): 'лемма_z',
            },
            ...
            'флексия_1': {
                ('шаблон_x', 'тип_основы_x'): None,
                ('шаблон_z', 'тип_основы_z'): None,
            },
            ...
        }.

        Таким образом, основы и флексии записываются в одну базу (в целях
        экономии); друг от друга их отличает наличие/отсутствие леммы.
        """

        def remove_accent(s):

            for c in 'ЀЍѐѝ́̀':
                s = s.replace(c, '')

            return s

        count = 0
        templates = set()

        for page in self.site.categories[self.category]:
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
                                    print(stem, template, name, page.name)

                                    # Типов бывает несколько
                                    data = self.db.setdefault(stem, {})
                                    data[(template, name)] = page.name
                                    self.db[stem] = data

                                    # Попутно собираем шаблоны
                                    templates.add(template)

                    # Конец раздела
                    elif line.startswith('='):
                        break

            count += 1
            if count > self.limit:
                break

        for template in templates:
            page = self.site.pages['Шаблон:' + template]
            lines = page.text().split(sep='\n')

            for i, line in enumerate(lines):
                if 'основа' in line:
                    sub = line[line.index('основа'):]
                    name = re.search('основа\d*(?=[|}])', sub).group()
                    infl = remove_accent(sub[sub.rindex('}') + 1:]).strip()

                    print(infl, template, name)

                    data = self.db.setdefault(infl, {})
                    data[(template, name)] = None
                    self.db[infl] = data

                    try:
                        if 'основа' not in lines[i + 1]:
                            break
                    except IndexError:
                        break


if __name__ == '__main__':
    w = Wiktioneer('ru_noun')
    w.scrape()
