from http.server import HTTPServer, CGIHTTPRequestHandler
import cgi
from searcher import Searcher
from indexer import Position


se = Searcher('w&p_vol_1-2')


class WPSE(CGIHTTPRequestHandler):

    @staticmethod
    def cit_pager(cit_off_lim, lim_cit, act):
        """
        Листает цитаты.

        :param cit_off_lim: список кортежей вида (оффсет по цитатам, лимит по цитатам) для каждого документа
        :param lim_cit: заданные либо извлечённые из формы лимиты по цитатам
        :param act: значение, извлечённое из формы
        :return: новый список кортежей (с обновлённым оффетом для одного из документов)
        """

        for i in range(len(cit_off_lim)):
            if act == 'prev_cit_%s' % i:
                new_off = max(0, cit_off_lim[i][0] - cit_off_lim[i][1] - 1)
                cit_off_lim[i] = (new_off, int(lim_cit[i]) - 1)
            elif act == 'home_cit_%s' % i:
                cit_off_lim[i] = (0, int(lim_cit[i]) - 1)
            elif act == 'next_cit_%s' % i:
                new_off = cit_off_lim[i][0] + cit_off_lim[i][1] + 1
                cit_off_lim[i] = (new_off, int(lim_cit[i]) - 1)

        return cit_off_lim

    @staticmethod
    def doc_pager(off, lim, act):
        """
        Листает документы.

        :param off: оффсет по документам
        :param lim: лимит по документам
        :param act: значение из формы
        :return: новый оффсет
        """

        if act == 'prev_doc':
            off -= lim
        elif act == 'home_doc':
            off = 1
        elif act == 'next_doc':
            off += lim

        return off

    def _set_headers(self, query='Start Page'):
        self.send_response(200)
        self.send_header('content-type', 'text/html')
        self.end_headers()
        self.wfile.write(('''<!DOCTYPE html>
<html lang="ru">
    <head>
        <title>WPSE • %s</title>
        <meta charset="utf-8">
        <style>
            body {
                background-color: AntiqueWhite;
                font-family: Georgia, serif;
                margin: 20px;
            }

            h1 {
                text-align: center;
            }

            .center {
                text-align: center;
                margin: auto;
                width: 50%%;
            }
        </style>
    </head>
''' % query).encode('utf-8'))

    def do_GET(self):
        self._set_headers()
        self.wfile.write('''
    <body>
        <h1><i>War & Peace</i> Search Engine</h1>
        <div class="center">
            <form method="post">
                <input type="text" name="query" placeholder="Enter your query">
                <button type="submit" name="action" value="submit">Submit</button>
            </form>
        </div>
    </body>
</html>'''.encode('utf-8'))

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD': 'POST', 'CONTENT_TYPE': self.headers['content-type']}
        )

        # Записываем запрос в переменную (в начале работы это `Start Page`)
        query = form.getfirst('query')
        # Список кортежей вида (оффсет по цитатам, лимит по цитатам)
        cit_off_lim = []

        # Если запрос не первый, то извлекаем соответствующие цифры из уже имеющейся формы
        if 'page_doc' in form.keys():
            # Оффсет и лимит по документам берём прямолинейно
            offset = int(form.getfirst('page_doc'))
            limit = int(form.getfirst('limit_doc'))

            # Оффсеты и лимиты по цитатам извлекаем для каждого документа по отдельности
            for i in range(limit):
                if form.getfirst('limit_cit_%s' % i):
                    limit_cit_i = int(form.getfirst('limit_cit_%s' % i))
                    offset_cit_i = (int(form.getfirst('page_cit_%s' % i)) - 1) * limit_cit_i + 1
                    cit_off_lim += [(offset_cit_i - 1, limit_cit_i - 1)]
                # Больше документов, чем в интервале от оффсета до оффсета плюс лимита, нам не нужно
                else:
                    break

            # Если же документов набралось меньше, то заполняем остаток значениями по умолчанию
            if len(cit_off_lim) < limit:
                for i in range(len(cit_off_lim) + 1, limit + 1):
                    cit_off_lim += [(0, 9)]

        # Если запрос первый, то присваиваем значения по умолчанию
        else:
            offset = 1
            limit = 2
            cit_off_lim = [(0, 9), (0, 9)]

        # Если делаем новый запрос, то оффсеты сбрасываем
        if form.getfirst('action') == 'submit':
            for i in range(limit):
                cit_off_lim[i] = (0, cit_off_lim[i][1])
            offset = 1
        # Если же пользуемся листалкой, то обновляем
        else:
            cit_off_lim = self.cit_pager(cit_off_lim, [form.getfirst('limit_cit_%s' % i) for i in range(limit)], form.getfirst('action'))
            offset = self.doc_pager(offset, limit, form.getfirst('action'))

        print(query, offset - 1, limit - 1, cit_off_lim)
        concord = se.tag(query, offset - 1, limit - 1, cit_off_lim)

        self._set_headers(query)
        self.wfile.write(('''
    <body>
        <h1><i>War & Peace</i> Search Engine</h1>
        <form method="post">
            <div class="center">
                <input type="text" name="query" placeholder="Enter your query" value="%s">
                <button type="submit" name="action" value="submit">Submit</button>
            </div>
            <ol>
        ''' % query).encode('utf-8'))

        for i, file in enumerate(concord.keys()):
            self.wfile.write(('''
                <li>
                    <b>%s</b>
                    <br>
                    <i>Navigation:</i>
                    <button type="submit" name="action" value="prev_cit_%s">&lt;</button>
                    <button type="submit" name="action" value="home_cit_%s">Home</button>
                    <button type="submit" name="action" value="next_cit_%s">&gt;</button>
                    ''' % (file, i, i, i)).encode('utf-8'))

            self.wfile.write(('''\
                    <i>Results per page:</i>
                    <input type="text" name="limit_cit_%s" value="%s" size="3" style="text-align: center;">''' %
                              (i, str(cit_off_lim[i][1] + 1))).encode('utf-8'))
            self.wfile.write(('''
                    <input type="hidden" name="page_cit_%s" value="%s">''' %
                              (i, str(((cit_off_lim[i][0] + 1) // (cit_off_lim[i][1] + 1)) + 1))).encode('utf-8'))
            self.wfile.write('''
                    <ol>'''.encode('utf-8'))

            for citation in concord[file]:
                self.wfile.write(('''
                        <li>%s</li>''' % citation).encode('utf-8'))

            self.wfile.write('''
                    </ol>
                </li>
                '''.encode('utf-8'))

        self.wfile.write(('''
                <br>
                <div class="center">
                    <i>Document navigation:</i>
                    <br>
                    <button type="submit" name="action" value="prev_doc">&lt;</button>
                    <button type="submit" name="action" value="home_doc">Home</button>
                    <button type="submit" name="action" value="next_doc">&gt;</button>
                    <br>
                    <i>Documents per page:</i>
                    <br>
                    <input type="text" name="limit_doc" value="%s" size="3" style="text-align: center;">
                    <input type="hidden" name="page_doc" value="%s">
                </div>
            </ol>
        </form>
    </body>
</html>''' % (str(limit), str(offset))).encode('utf-8'))


def run(server_class=HTTPServer, handler_class=WPSE, port=8080):

    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()


if __name__ == '__main__':
    run()
