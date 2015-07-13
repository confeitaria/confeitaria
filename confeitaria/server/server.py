import os
import binascii

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

    def run(self, force=True):
        """
        This method starts the server up serving the given page.
        A page is an object of a class as the one below:

        >>> class TestPage(object):
        ...     def index(self):
        ...         return "This is a test"

        To run it, just call `Server.run()`, as in:

        >>> s = Server(TestPage())

        >>> import multiprocessing, waiters
        >>> p = multiprocessing.Process(target=s.run)
        >>> p.start()
        >>> waiters.wait_server_up('', s.port)

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
        while True:
            try:
                httpd = simple_server.make_server('', self.port, self.respond)
                print "Serving on port 8000..."
                httpd.serve_forever()
            except socket.error:
                if not force:
                    raise

    def respond(self, environ, start_response):
        cookies = Cookie.SimpleCookie(environ.get('HTTP_COOKIE', ''))
        status = '200 OK'
        headers = [('Content-type', 'text/html')]

        try:
            content = ''
            request = self.request_parser.parse_request(environ)
            page = request.page

            if hasattr(page, 'set_request'):
                page.set_request(request)

            if hasattr(page, 'set_cookies'):
                page.set_cookies(cookies)

            if hasattr(page, 'set_session'):
                if 'SESSIONID' not in cookies:
                    session_id = binascii.hexlify(os.urandom(16))
                    cookies['SESSIONID'] = session_id
                else:
                    session_id = cookies['SESSIONID'].value

                if session_id not in self.sessions:
                    self.sessions[session_id] = {}

                page.set_session(self.sessions[session_id])

            if request.method == 'GET':
                content = page.index(*request.args, **request.kwargs)
            elif request.method == 'POST':
                page.action(*request.args, **request.kwargs)
                raise confeitaria.responses.SeeOther()
        except confeitaria.responses.Response as e:
            status = e.status_code
            headers = e.headers
            if e.status_code.startswith('30'):
                headers = replace_none_location(headers, request.url)

        headers.extend(get_cookies_tuples(cookies))
        start_response(status, headers)

        return content

    def __enter__(self):
        import multiprocessing
        import waiters

        try:
            self._process = multiprocessing.Process(target=self.run)
            self._process.start()
            waiters.wait_server_up('', self.port)
        except:
            raise

    def __exit__(self, type, value, traceback):
        import waiters

        self._process.terminate()
        waiters.wait_server_down('', self.port)
        self._process = None

def get_cookies_tuples(cookies):
    """
    Returns an iterator. This iterator yields tuples - each tuple defines a
    cookie and is appropriate to be put in the headers list for
    ``wsgiref.start_response()``::

    >>> cookie = Cookie.SimpleCookie()
    >>> cookie['a'] = 'A'
    >>> cookie['b'] = 'B'
    >>> list(get_cookies_tuples(cookie))
    [('Set-Cookie', 'a=A'), ('Set-Cookie', 'b=B')]
    """
    return (
        ('Set-Cookie', cookies[k].OutputString()) for k in cookies
    )

def replace_none_location(headers, location):
    """
    Returns a new list of tuples (with headers values) where any 'Location'
    header with ``None`` as value is replaced by the given location::

    >>> headers = [('Location', None), ('Set-Cookie', 'a=A')]
    >>> replace_none_location(headers, '/b')
    [('Location', '/b'), ('Set-Cookie', 'a=A')]

    Location headers already set are not affected::

    >>> headers = [('Location', '/a'), ('Set-Cookie', 'a=A')]
    >>> replace_none_location(headers, '/b')
    [('Location', '/a'), ('Set-Cookie', 'a=A')]

    """
    return [
        (
            h[0],
            location if (h[0].lower() == 'location') and (h[1] is None) else h[1]
        )
        for h in headers
    ]
