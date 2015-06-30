import unittest
import doctest
import Cookie

import requests

from confeitaria.reference.tests import TestReference
from ..server import Server, get_cookies_tuples
from confeitaria.server import server
from confeitaria import runner

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
        time.sleep(1)

        request = requests.get('http://localhost:8000/')
        self.assertEquals('page content', request.text)
        self.assertEquals(200, request.status_code)
        self.assertEquals('text/html', request.headers['content-type'])

        process.terminate()

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

test_suite = unittest.TestLoader().loadTestsFromTestCase(TestServer)
test_suite.addTest(
    unittest.TestLoader().loadTestsFromTestCase(TestServerFunctions)
)
test_suite.addTest(doctest.DocTestSuite(server))
test_suite.addTest(doctest.DocTestSuite(runner))
test_suite.addTest(
    doctest.DocFileSuite(
        'doc/index.rst', module_relative=True, package=confeitaria
    )
)

def load_tests(loader, tests, ignore):
    return test_suite
