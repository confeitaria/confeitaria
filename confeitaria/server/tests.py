import unittest

import requests

from ..server import Server

class TestServer(unittest.TestCase):

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

    def test_attributes_as_subpages(self):
        """
        This test ensures that when a path is requested to the server it will
        access subpages (that is, pages that are attributes of other pages).
        """
        class RootPage(object):
            def index(self):
                return 'page: root'

        class SubPage(object):
            def index(self):
                return 'page: sub'

        class AnotherSubPage(object):
            def index(self):
                return 'page: another'

        root = RootPage()
        root.sub = SubPage()
        root.sub.another = AnotherSubPage()

        with Server(root):
            r = requests.get('http://localhost:8080/')
            self.assertEquals('page: root', r.text)
            r = requests.get('http://localhost:8080/sub')
            self.assertEquals('page: sub', r.text)
            r = requests.get('http://localhost:8080/sub/another')
            self.assertEquals('page: another', r.text)

    def test_index_parameters_from_request(self):
        """
        This test ensures that an index() method with parameters (other than
        ``self``) will get these parameters from the query string. These
        arguments should have default values.
        """
        class TestPage(object):
            def index(self, kwarg=None):
                return 'kwarg: {0}'.format(kwarg)

        with Server(TestPage()):
            r = requests.get('http://localhost:8080/?kwarg=example')
            self.assertEquals('kwarg: example', r.text)

    def test_index_parameters_from_path(self):
        """
        This test ensures that an index method with non-optional parameters
        other than ``self`` can have they filled by the query path'.
        """
        class TestPage(object):
            def index(self, arg):
                return 'arg: {0}'.format(arg)

        with Server(TestPage()):
            r = requests.get('http://localhost:8080/example')
            self.assertEquals('arg: example', r.text)

    def test_index_parameters_from_path_more_than_one(self):
        """
        This test ensures that all non-optional parameters from index will be
        get from the query path.
        """
        class TestPage(object):
            def index(self, arg1, arg2):
                return 'arg1: {0}; arg2: {1}'.format(arg1, arg2)

        with Server(TestPage()):
            r = requests.get('http://localhost:8080/first/second')
            self.assertEquals('arg1: first; arg2: second', r.text)

    def test_index_parameters_from_path_and_query_args(self):
        """
        This test ensures that positional parameters will  be get from query
        path and the optional ones will be get from the query string
        """
        class TestPage(object):
            def index(self, arg1, arg2, kwarg1=None, kwarg2=None):
                result = 'arg1={0}; arg2={1}'.format(arg1, arg2)
                if kwarg1 is not None:
                    result += '; kwarg1={2}'
                if kwarg2 is not None:
                    result += '; kwarg2={3}'
                return result.format(arg1, arg2, kwarg1, kwarg2)

        with Server(TestPage()):
            r = requests.get('http://localhost:8080/one/cake')
            self.assertEquals('arg1=one; arg2=cake', r.text)
            r = requests.get(
                'http://localhost:8080/this/pie?kwarg2=tasty&kwarg1=is'
            )
            self.assertEquals(
                'arg1=this; arg2=pie; kwarg1=is; kwarg2=tasty', r.text
            )

if __name__ == "__main__":
    unittest.main()
