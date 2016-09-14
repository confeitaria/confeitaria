import unittest
import Cookie

import requests

from confeitaria_tests.reference import TestReference
from confeitaria.server.server import Server, get_cookies_tuples, replace_none_location
from inelegant.net import wait_server_up, wait_server_down
from confeitaria.server import server
from confeitaria.runner import runner

import confeitaria
import confeitaria.interfaces

class TestServer(TestReference):

    def test_serve_page(self):
        import multiprocessing
        import time

        class TestPage(object):
            def index(self):
                return 'page content'

        page = TestPage()
        server = Server(page)

        process = multiprocessing.Process(target=server.run)
        process.start()
        wait_server_up('', 8000, tries=10000)

        request = requests.get('http://localhost:8000/')
        self.assertEquals('page content', request.text)
        self.assertEquals(200, request.status_code)
        self.assertEquals('text/html', request.headers['content-type'])

        process.terminate()
        wait_server_down('', 8000, tries=10000)

    def test_with(self):
        """
        The Server object should be compatible with the `with` clause.
        """
        class TestPage(object):
            def index(self):
                return 'page content'

        page = TestPage()

        with Server(page):
            request = requests.get('http://localhost:8000/')
            self.assertEquals('page content', request.text)
            self.assertEquals(200, request.status_code)
            self.assertEquals('text/html', request.headers['content-type'])

    def test_handle_old_session_id_from_cookie_after_restart(self):
        """
        Since the default session is stored in memory, it is lost when the
        server restarts. Yet, a browser can still have the session id from the
        first execution of the server. If that happens, the server should handle
        it gracefully.
        """
        class TestPage(confeitaria.interfaces.SessionedPage):
            def index(self):
                return ''

        page = TestPage()

        with Server(page):
            request = requests.get('http://localhost:8000/')

            request = requests.get(
                'http://localhost:8000/', cookies=request.cookies
            )
            self.assertEquals(200, request.status_code)

        with Server(page):
            request = requests.get(
                'http://localhost:8000/', cookies=request.cookies
            )
            self.assertEquals(200, request.status_code)

    def get_server(self, page):
        return Server(page)

class TestServerFunctions(unittest.TestCase):

    def test_get_cookies_tuples(self):
        """
        Ensures the ``get_cookies_list()`` returns an iterator yielding tuples
        appropriate to be added to a header.
        """
        cookie = Cookie.SimpleCookie()
        cookie['a'] = 'A'
        cookie['b'] = 'B'

        i = get_cookies_tuples(cookie)

        self.assertEquals(i.next(), ('Set-Cookie', 'a=A'))
        self.assertEquals(i.next(), ('Set-Cookie', 'b=B'))

    def test_replace_none_location(self):
        """
        Ensures that the function replaces locations from a header which are
        ``None`` with a valid location.
        """
        headers = [('Location', '/a'), ('Set-Cookie', 'a=A')]
        self.assertEquals(
            [('Location', '/a'), ('Set-Cookie', 'a=A')],
            replace_none_location(headers, '/b')
        )

        headers = [('Location', None), ('Set-Cookie', 'a=A')]
        self.assertEquals(
            [('Location', '/b'), ('Set-Cookie', 'a=A')],
            replace_none_location(headers, '/b')
        )

import inelegant.finder

load_tests = inelegant.finder.TestFinder(
    __name__, server, runner, skip=TestReference
).load_tests

if __name__ == "__main__":
    unittest.main()
