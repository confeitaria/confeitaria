import unittest

import requests

from ..server import Server

class SimplestTestPage(object):

    def index(self):
        return 'simplest test server'

class TestServer(unittest.TestCase):

    def test_serve_page(self):
        import multiprocessing
        import time

        page = SimplestTestPage()
        server = Server(page)

        process = multiprocessing.Process(target=server.run)
        process.start()
        time.sleep(1)

        request = requests.get('http://localhost:8080/')
        self.assertEquals(u'simplest test server', request.text)
        self.assertEquals(200, request.status_code)
        self.assertEquals('text/html', request.headers['content-type'])

        process.terminate()

    def test_with(self):
        """
        The Server object should be compatible with the `with` clause.
        """
        page = SimplestTestPage()

        with Server(page):
            request = requests.get('http://localhost:8080/')
            self.assertEquals(u'simplest test server', request.text)
            self.assertEquals(200, request.status_code)
            self.assertEquals('text/html', request.headers['content-type'])

    def test_attributes_as_subpages(self):
        """
        This test ensures that when a path is requested to the server it will
        access subpages (that is, pages that are attributes of other pages).
        """
        class RootPage(object):
            def index(self):
                return 'root'

        class SubPage(object):
            def index(self):
                return 'a subpage'

        class SubSubPage(object):
            def index(self):
                return 'another subpage'

        root = RootPage()
        root.sub = SubPage()
        root.sub.another = SubSubPage()

        with Server(root):
            r = requests.get('http://localhost:8080/')
            self.assertEquals(u'root', r.text)
            r = requests.get('http://localhost:8080/sub')
            self.assertEquals(u'a subpage', r.text)
            r = requests.get('http://localhost:8080/sub/another')
            self.assertEquals(u'another subpage', r.text)

    def test_index_parameters_from_request(self):
        """
        This test ensures that an index() method with parameters (other than
        ``self``) will get these parameters from the query string. These
        arguments should have default values.
        """
        class TestPage(object):
            def index(self, content=None):
                return 'The content is ' + content

        with Server(TestPage()):
            r = requests.get('http://localhost:8080/?content=example')
            self.assertEquals('The content is example', r.text)

    def test_index_parameters_from_path(self):
        """
        This test ensures that an index method with non-optional parameters
        other than ``self`` can have they filled by the query path'.
        """
        class TestPage(object):
            def index(self, positional_param):
                return 'The positional parameter is ' + positional_param

        with Server(TestPage()):
            r = requests.get('http://localhost:8080/example')
            self.assertEquals('The positional parameter is example', r.text)

if __name__ == "__main__":
    unittest.main()
