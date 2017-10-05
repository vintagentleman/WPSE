import shelve
from mwclient import Site


def scrape(category, database):
    site = Site(('https', 'ru.wiktionary.org'))
    with shelve.open(database) as db:

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
                                # В основах избавляемся от лишних же пробелов и ударения
                                stem = item[item.index('=') + 1:].strip().replace('́', '')
                                if stem:
                                    # Типов м. б. несколько (?)
                                    data = db.setdefault(stem, [])
                                    data.append(template)
                                    db[stem] = data

                    # Конец раздела
                    elif line.startswith('='):
                        break


if __name__ == '__main__':
    scrape('Слова_латинского_происхождения', 'latin')
