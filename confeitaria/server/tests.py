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

    def test_index_parameters_from_path_more_than_one(self):
        """
        This test ensures that all non-optional parameters from index will be
        get from the query path.
        """
        class TestPage(object):
            def index(self, n1, operation, n2):
                if operation == "+":
                    result = int(n1) + int(n2)
                elif operation == "-":
                    result = int(n1) - int(n2)
                else:
                    result = 'undefined'
                return 'The result of {0}{1}{2} is {3}'.format(
                    n1, operation, n2, result)

        with Server(TestPage()):
            r = requests.get('http://localhost:8080/3/+/2')
            self.assertEquals('The result of 3+2 is 5', r.text)
            r = requests.get('http://localhost:8080/3/-/2')
            self.assertEquals('The result of 3-2 is 1', r.text)
            r = requests.get('http://localhost:8080/3/;/2')
            self.assertEquals('The result of 3;2 is undefined', r.text)

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
