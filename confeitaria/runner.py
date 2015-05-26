import functools
import wsgiref.simple_server as simple_server

from server import Server

DEFAULT_CONFIG = {
    'port': 8000
}

def page_server(page, environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'text/html')]

    start_response(status, headers)

    return page.index()

def run(page, config=None):
    """
    This is the simplest way so far of running a Confeitaria site.
    ``confeitaria.run()`` starts up a server to serve the output of a page.

    A page is an object of a class as the one below:

    >>> class TestPage(object):
    ...     def index(self):
    ...         return "This is a test"

    To run it, just call `confeitaria.run()`, as in:

    >>> def start():
    ...    test_page = TestPage()
    ...    run(test_page)

    >>> import multiprocessing, time
    >>> p = multiprocessing.Process(target=start)
    >>> p.start()
    >>> time.sleep(1)

    Then the server is supposed to serve the content provided by the page:

    >>> import requests
    >>> r = requests.get('http://localhost:8080/')
    >>> r.text
    u'This is a test'
    >>> r.status_code
    200
    >>> r.headers['content-type']
    'text/html'

    >>> p.terminate()
    """
    config = DEFAULT_CONFIG if config is None else config

    server = Server(page, **config).run()
