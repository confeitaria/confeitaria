import os
import binascii
import multiprocessing
import time

import wsgiref.simple_server as simple_server
import Cookie

import requestparser

import confeitaria.request
import confeitaria.responses

class Server(object):
    """
    The ``Server`` objects listen to HTTP requests and serve responses according
    to the page object returned values.
    """

    def __init__(self, page, port=8000):
        self.request_parser = requestparser.RequestParser(page)
        self.port = port
        self.sessions = {}
        self._process = None

    def run(self):
        """
        This method starts the server up serving the given page.
        A page is an object of a class as the one below:

        >>> class TestPage(object):
        ...     def index(self):
        ...         return "This is a test"

        To run it, just call `Server.run()`, as in:

        >>> s = Server(TestPage())

        >>> import multiprocessing, time
        >>> p = multiprocessing.Process(target=s.run)
        >>> p.start()
        >>> time.sleep(1)

        Then the server is supposed to serve the content provided by the page:

        >>> import requests
        >>> r = requests.get('http://localhost:8000/')
        >>> r.text
        u'This is a test'
        >>> r.status_code
        200
        >>> r.headers['content-type']
        'text/html'

        >>> p.terminate()

        You can also, mostly for testing purposes, start up a server through a
        ``with`` statement:

        >>> with Server(TestPage()):
        ...     r = requests.get("http://localhost:8000")
        ...     r.text
        u'This is a test'
        """
        httpd = simple_server.make_server('', self.port, self._run_app)
        print "Serving on port 8000..."
        httpd.serve_forever()

    def _run_app(self, environ, start_response):
        path_info = environ.get('PATH_INFO', '')
        query_string = environ.get('QUERY_STRING', '')
        url = path_info + ('?' + query_string if query_string else '')

        cookies = Cookie.SimpleCookie(environ.get('HTTP_COOKIE', ''))
        status = '200 OK'
        headers = [('Content-type', 'text/html')]

        try:
            content = ''
            request = self.request_parser.parse_request(
                url, self._get_body_content(environ)
            )
            page = request.page

            if hasattr(page, 'set_request'):
                page.set_request(request)

            if hasattr(page, 'set_cookies'):
                page.set_cookies(cookies)

            if hasattr(page, 'set_session'):
                if 'SESSIONID' not in cookies:
                    session_id = binascii.hexlify(os.urandom(16))
                    self.sessions[session_id] = {}
                    cookies['SESSIONID'] = session_id
                else:
                    session_id = cookies['SESSIONID'].value

                page.set_session(self.sessions[session_id])

            if environ['REQUEST_METHOD'] == 'GET':
                content = page.index(*request.args, **request.kwargs)
                self._add_cookies_to_headers(cookies, headers)
            elif environ['REQUEST_METHOD'] == 'POST':
                page.action(*request.args, **request.kwargs)
                raise confeitaria.responses.SeeOther()
        except confeitaria.responses.Response as e:
            if e.status_code.startswith('30'):
                self._replace_none_location(e.headers, url)
            status = e.status_code
            self._add_cookies_to_headers(cookies, e.headers)
            headers = e.headers

        start_response(status, headers)

        return content

    def _add_cookies_to_headers(self, cookies, headers):
        headers.extend(
            ('Set-Cookie', cookies[k].OutputString()) for k in cookies
        )

    def _get_body_content(self, environ):
        if environ['REQUEST_METHOD'] != 'POST':
            return None
        try:
            body_size = int(environ.get('CONTENT_LENGTH', 0))
        except (ValueError):
            body_size = 0

        return environ['wsgi.input'].read(body_size)

    def _replace_none_location(self, headers, location):
        for i, h in enumerate(headers):
            if (h[0].lower() == 'location') and (h[1] is None):
                headers[i] = h[0], location

    def __enter__(self):
        self._process = multiprocessing.Process(target=self.run)
        self._process.start()
        time.sleep(1)

    def __exit__(self, type, value, traceback):
        self._process.terminate()
        self._process = None

