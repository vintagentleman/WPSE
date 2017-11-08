from http.server import HTTPServer, CGIHTTPRequestHandler
import cgi
from searcher import Searcher


class WPSE(CGIHTTPRequestHandler):

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

        query = form.getfirst('query')
        cit_off_lim = []

        if 'page_doc' in form.keys():
            offset = int(form.getfirst('page_doc'))
            limit = int(form.getfirst('limit_doc'))

            for i in range(limit):
                if form.getfirst('limit_cit_%s' % i):
                    limit_cit_i = int(form.getfirst('limit_cit_%s' % i))
                    offset_cit_i = (int(form.getfirst('page_cit_%s' % i)) - 1) * limit_cit_i + 1
                    cit_off_lim += [(offset_cit_i - 1, limit_cit_i - 1)]
                else:
                    break

            if len(cit_off_lim) < limit:
                for i in range(len(cit_off_lim) + 1, limit + 1):
                    cit_off_lim += [(0, 9)]

        else:
            offset = 1
            limit = 2
            cit_off_lim = [(0, 9), (0, 9)]

        for i in range(limit):
            if form.getfirst('action') == 'prev_cit_%s' % i:
                new_off = max(0, cit_off_lim[i][0] - cit_off_lim[i][1] - 1)
                cit_off_lim[i] = (new_off, int(form.getfirst('limit_cit_%s' % i)) - 1)
            elif form.getfirst('action') == 'home_cit_%s' % i:
                cit_off_lim[i] = (0, int(form.getfirst('limit_cit_%s' % i)) - 1)
            elif form.getfirst('action') == 'next_cit_%s' % i:
                new_off = cit_off_lim[i][0] + cit_off_lim[i][1] + 1
                cit_off_lim[i] = (new_off, int(form.getfirst('limit_cit_%s' % i)) - 1)

        if form.getfirst('action') == 'prev_doc':
            offset -= limit
        elif form.getfirst('action') == 'home_doc':
            offset = 1
        elif form.getfirst('action') == 'next_doc':
            offset += limit

        if form.getfirst('action') == 'submit':
            for i in range(limit):
                cit_off_lim[i] = (0, cit_off_lim[i][1])
            offset = 1

        print(query, offset - 1, limit - 1, cit_off_lim)

        se = Searcher('turgenev')
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
                    <button type="submit" name="action" value="prev_cit_%s">&lt;</button>
                    <button type="submit" name="action" value="home_cit_%s">•</button>
                    <button type="submit" name="action" value="next_cit_%s">&gt;</button>
                    <br>
            ''' % (i, i, i)).encode('utf-8'))

            self.wfile.write(('''
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
                </li>'''.encode('utf-8'))

        self.wfile.write(('''
                <div class="center">
                    <button type="submit" name="action" value="prev_doc">&lt;</button>
                    <button type="submit" name="action" value="home_doc">•••</button>
                    <button type="submit" name="action" value="next_doc">&gt;</button>
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
