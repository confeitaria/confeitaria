import functools
import wsgiref.simple_server as simple_server

from server import Server

def run(page):
    """
    This is the simplest way so far of running a Confeitaria site.
    ``confeitaria.run()`` starts up a server to serve the output of a page.

    A page is an object of a class as the one below:

    >>> class TestPage(object):
    ...     def index(self):
    ...         return "This is a test"

    To run it, just call `confeitaria.run()`, as in:

    >>> def start():
    ...    from inelegant.net import wait_server_down
    ...    wait_server_down('', 8000)
    ...    test_page = TestPage()
    ...    run(test_page)

    >>> import multiprocessing
    >>> from inelegant.net import wait_server_up
    >>> p = multiprocessing.Process(target=start)
    >>> p.start()
    >>> wait_server_up('', 8000)

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
    """
    server = Server(page).run()
