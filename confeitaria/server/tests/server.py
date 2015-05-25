import unittest
import doctest

import requests

from confeitaria.reference.tests import TestReference
from ..server import Server
from confeitaria.server import server
from confeitaria import runner

import confeitaria

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

        request = requests.get('http://localhost:8080/')
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
            request = requests.get('http://localhost:8080/')
            self.assertEquals('page content', request.text)
            self.assertEquals(200, request.status_code)
            self.assertEquals('text/html', request.headers['content-type'])

    def get_server(self, page):
        return Server(page)

test_suite = unittest.TestLoader().loadTestsFromTestCase(TestServer)
test_suite.addTest(doctest.DocTestSuite(server))
test_suite.addTest(doctest.DocTestSuite(runner))
test_suite.addTest(
    doctest.DocFileSuite(
        'doc/index.rst', module_relative=True, package=confeitaria
    )
)

def load_tests(loader, tests, ignore):
    tests.addTest(test_suite)

    return tests
