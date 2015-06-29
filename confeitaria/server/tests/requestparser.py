import unittest
import doctest

try:
    import cStringIO as StringIO
except:
    import StringIO

import requests

from ..requestparser import RequestParser
from confeitaria.responses import NotFound

import confeitaria.server.requestparser

class TestRequestParser(unittest.TestCase):

    def test_parse_empty_dict(self):
        """
        ``RequestParser`` should parse the environment dict. It should also be
        able to parser an empty environment - and this test checks that.
        """
        class TestPage(object):
            def index(self):
                return ''

        page = TestPage()
        request_parser = RequestParser(page)
        request = request_parser.parse_request({})
        self.assertEquals(page, request.page)
        self.assertEquals([], request.path_args)
        self.assertEquals({}, request.query_args)
        self.assertEquals({}, request.form_args)
        self.assertEquals([], request.args)
        self.assertEquals({}, request.kwargs)
        self.assertEquals('GET', request.method)

    def test_get_root(self):
        """
        This test ensures that the root path (``/``) is mapped to the root page.
        """
        class TestPage(object):
            def index(self):
                return ''

        page = TestPage()
        request_parser = RequestParser(page)
        request = request_parser.parse_request({'PATH_INFO': '/'})
        self.assertEquals(page, request.page)
        self.assertEquals([], request.path_args)
        self.assertEquals({}, request.query_args)
        self.assertEquals({}, request.form_args)
        self.assertEquals([], request.args)
        self.assertEquals({}, request.kwargs)

    def test_subpage_not_found_404(self):
        """
        This test ensures that, if a non-existence page is requested, an
        exception reporting a 404 Not Found status is raised.
        """
        class TestPage(object):
            def index(self):
                return ''

        page = TestPage()
        request_parser = RequestParser(page)

        with self.assertRaises(NotFound):
            request_parser.parse_request({'PATH_INFO': '/nosub'})

    def test_not_subpage_404(self):
        """
        This test ensures that, if the attribute corresponding to the path is
        not a page, then a 404 Not Found status is raised..
        """
        class TestPage(object):
            def index(self):
                return ''

        page = TestPage()
        page.nosub = object()
        request_parser = RequestParser(page)

        with self.assertRaises(NotFound):
            request_parser.parse_request({'PATH_INFO': '/nosub'})

    def test_path_args(self):
        """
        This test ensures that the parser can find parameters in path.
        """
        class TestPage(object):
            def index(self, arg):
                return ''

        page = TestPage()
        request_parser = RequestParser(page)
        request = request_parser.parse_request({'PATH_INFO': '/value'})

        self.assertEquals(page, request.page)
        self.assertEquals(['value'], request.path_args)
        self.assertEquals({}, request.query_args)
        self.assertEquals({}, request.form_args)
        self.assertEquals(['value'], request.args)
        self.assertEquals({}, request.kwargs)

    def test_missing_path_args_not_found_404(self):
        """
        This test ensures that  parser finds a page whose index method
        expects arguments, but the parameters are not passed in the path,
        the the arguments values will be ``None``.
        """
        class TestPage(object):
            def index(self, arg):
                return ''

        page = TestPage()
        request_parser = RequestParser(page)

        with self.assertRaises(NotFound):
            request_parser.parse_request({'PATH_INFO': '/'})

    def test_too_many_path_parameters_leads_to_404(self):
        """
        This test ensures that when parser finds a page whose index method
        expects arguments, but the number of parameters in the path is larger
        than the number of arguments in the index method, then a 404 Not Found
        response will follow

        """
        class TestPage(object):
            def index(self, arg):
                return ''

        page = TestPage()
        request_parser = RequestParser(page)
        request = request_parser.parse_request({'PATH_INFO': '/value'})

        self.assertEquals(page, request.page)
        self.assertEquals(['value'], request.path_args)
        self.assertEquals(['value'], request.args)

        with self.assertRaises(NotFound):
            request_parser.parse_request({'PATH_INFO': '/value/excess'})


    def test_query_args(self):
        """
        This test ensures that when parser finds a page whose index method
        expects arguments, but the number of parameters in the path is larger
        than the number of arguments in the index method, then a 404 Not Found
        response will follow.
        """
        class TestPage(object):
            def index(self, kwarg1=None, kwarg2=None):
                return ''

        page = TestPage()
        request_parser = RequestParser(page)
        request = request_parser.parse_request({
            'PATH_INFO': '/', 'QUERY_STRING': 'kwarg2=value'
        })

        self.assertEquals(page, request.page)
        self.assertEquals([], request.path_args)
        self.assertEquals({'kwarg2': 'value'}, request.query_args)
        self.assertEquals({}, request.form_args)
        self.assertEquals({'kwarg2': 'value'}, request.kwargs)

    def test_kwargs_ignores_values_not_in_method_signature(self):
        """
        This method ensures that the ``Request.kwargs`` dict has no argument
        whose name is not a name of a positional argument of the method to be
        called.
        """
        class TestPage(object):
            def index(self, kwarg=None):
                return ''

        page = TestPage()
        request_parser = RequestParser(page)
        request = request_parser.parse_request({
            'PATH_INFO': '/', 'QUERY_STRING': 'kwarg=value&arg=no'
        })

        self.assertEquals(page, request.page)
        self.assertEquals({'kwarg': 'value', 'arg': 'no'}, request.query_args)
        self.assertEquals({'kwarg': 'value'}, request.kwargs)

    def test_kwags_has_no_values_to_positional_arguments(self):
        """
        This method ensures that the ``Request.kwargs`` dict has no argument
        that should be specified as path arguments.
        """
        class TestPage(object):
            def index(self, arg, kwarg=None):
                return ''

        page = TestPage()
        request_parser = RequestParser(page)
        request = request_parser.parse_request({
            'PATH_INFO': '/example', 'QUERY_STRING': 'kwarg=value&arg=no'
        })

        self.assertEquals(page, request.page)
        self.assertEquals(['example'], request.path_args)
        self.assertEquals(['example'], request.args)
        self.assertEquals({'kwarg': 'value', 'arg': 'no'}, request.query_args)
        self.assertEquals({'kwarg': 'value'}, request.kwargs)

    def test_path_and_query_args(self):
        """
        This test checks whether path and query args are being properly parsed.
        """
        class TestPage(object):
            def index(self, arg1, arg2, kwarg1=None, kwarg2=None):
                return ''

        page = TestPage()
        request_parser = RequestParser(page)
        request = request_parser.parse_request({
            'PATH_INFO': '/value1/value2', 'QUERY_STRING': 'kwarg2=value'
        })

        self.assertEquals(page, request.page)
        self.assertEquals(['value1', 'value2'], request.path_args)
        self.assertEquals({'kwarg2': 'value'}, request.query_args)
        self.assertEquals({}, request.form_args)
        self.assertEquals(['value1', 'value2'], request.args)
        self.assertEquals({'kwarg2': 'value'}, request.kwargs)

    def test_attribute_has_precedence_over_path_parameters(self):
        """
        If a page has both an index method with arguments and an attribute, the
        attribute should have precedence over the arguments when parsing path
        parameters.
        """
        class RootPage(object):
            def index(self, arg):
                return 'page: root, arg: {0}'.format(arg)
        class AttributePage(object):
            def index(self):
                return 'page: attribute'

        page = RootPage()
        page.attribute = AttributePage()
        request_parser = RequestParser(page)

        request = request_parser.parse_request({'PATH_INFO': '/value'})

        self.assertEquals(page, request.page)
        self.assertEquals(['value'], request.args)
        self.assertEquals(
            'page: root, arg: value',
            request.page.index(*request.args, **request.kwargs)
        )

        request = request_parser.parse_request({'PATH_INFO': '/attribute'})

        self.assertEquals(page.attribute, request.page)
        self.assertEquals([], request.args)
        self.assertEquals(
            'page: attribute',
            request.page.index(*request.args, **request.kwargs)
        )

    def test_action_method_creates_page(self):
        """
        If an object has an ``action()`` bound method, the object is a page -
        one that only handles POST requests.
        """
        class RootPage(object):
            def index(self, arg):
                return 'page: root, arg: {0}'.format(arg)
        class ActionPage(object):
            def action(self):
                pass

        page = RootPage()
        page.sub = ActionPage()
        request_parser = RequestParser(page)

        request = request_parser.parse_request({
            'REQUEST_METHOD': 'POST', 'PATH_INFO': '/sub',
            'CONTENT_LENGTH': 0, 'wsgi.input': StringIO.StringIO()
        })

        self.assertEquals(page.sub, request.page)

    def test_action_method_returns_parsed_body(self):
        """
        The contents of a POST request should be parsed.
        """
        class RootPage(object):
            def index(self, arg):
                return 'page: root, arg: {0}'.format(arg)
        class ActionPage(object):
            def action(self, kwarg=None):
                pass

        page = RootPage()
        page.sub = ActionPage()
        request_parser = RequestParser(page)

        request = request_parser.parse_request({
            'REQUEST_METHOD': 'POST', 'PATH_INFO': '/sub',
            'CONTENT_LENGTH': len('kwarg=example'),
            'wsgi.input': StringIO.StringIO('kwarg=example')
        })

        self.assertEquals({}, request.query_args)
        self.assertEquals({'kwarg': 'example'}, request.form_args)
        self.assertEquals({'kwarg': 'example'}, request.kwargs)

    def test_returned_tuple_is_request_object(self):
        """
        The tuple returned by the parser should also be a request object.
        """
        class TestPage(object):
            def index(self, kwarg=None):
                return ''

        page = TestPage()
        request_parser = RequestParser(page)
        request = request_parser.parse_request({
            'PATH_INFO': '/', 'QUERY_STRING': 'kwarg=value&kwarg1=example'
        })

        self.assertEquals(
            {'kwarg': 'value', 'kwarg1': 'example'}, request.query_args
        )

    def test_request_not_tuple_anymore(self):
        """
        In the past, the request object used to be a tuple. It proved to be
        confusing. As a consequence, we removed this behavior from it. This test
        registers this change.
        """
        class TestPage(object):
            def index(self):
                return ''

        page = TestPage()
        request_parser = RequestParser(page)

        with self.assertRaises(TypeError):
            _, _, _ = request_parser.parse_request({'PATH_INFO': '/'})


    def test_request_has_url(self):
        """
        The request object should have the called URL.
        """
        class TestPage(object):
            def index(self):
                return ''

        page = TestPage()
        page.sub = TestPage()
        request_parser = RequestParser(page)

        request = request_parser.parse_request({'PATH_INFO': '/'})
        self.assertEquals('/', request.url)

        request = request_parser.parse_request({
            'PATH_INFO': '/', 'QUERY_STRING': 'arg=1'
        })
        self.assertEquals('/?arg=1', request.url)

        request = request_parser.parse_request({'PATH_INFO': '/sub'})
        self.assertEquals('/sub', request.url)

    def test_get_http_method_yields_index_page_no_action_page(self):
        """
        Requiring a page with an index method (but no action method) with the
        ``GET`` HTTP method should work, but requiring it with the ``POST``
        method should fail.
        """
        class IndexPage(object):
            def index(self):
                return ''

        request_parser = RequestParser(IndexPage())

        request = request_parser.parse_request({'REQUEST_METHOD': 'GET'})
        with self.assertRaises(confeitaria.responses.MethodNotAllowed):
            request_parser.parse_request({'REQUEST_METHOD': 'POST'})

    def test_post_http_method_yields_action_page_no_index_page(self):
        """
        Requiring a page with an action method (but no index method) with the
        ``POST`` HTTP method should work, but requiring it with the ``GET``
        method should fail.
        """
        class ActionPage(object):
            def action(self):
                pass

        request_parser = RequestParser(ActionPage())

        request = request_parser.parse_request({'REQUEST_METHOD': 'POST'})
        with self.assertRaises(confeitaria.responses.MethodNotAllowed):
            request_parser.parse_request({'REQUEST_METHOD': 'GET'})

    def test_request_has_request_method(self):
        """
        The request object should have the request method.
        """
        class TestPage(object):
            def index(self):
                return ''
            def action(self):
                pass

        page = TestPage()
        page.sub = TestPage()
        request_parser = RequestParser(page)

        request = request_parser.parse_request({'REQUEST_METHOD': 'GET'})
        self.assertEquals('GET', request.method)

        request = request_parser.parse_request({'REQUEST_METHOD': 'POST'})
        self.assertEquals('POST', request.method)

    def test_other_http_methods_yield_method_not_allowed(self):
        """
        Requiring a page with an index method (but no action method) with the
        ``GET`` HTTP method should work, but requiring it with the ``POST``
        method should fail.
        """
        class TestPage(object):
            def index(self):
                return ''
            def action(self):
                pass

        request_parser = RequestParser(TestPage())

        with self.assertRaises(confeitaria.responses.MethodNotAllowed):
            request_parser.parse_request({'REQUEST_METHOD': 'PUT'})
        with self.assertRaises(confeitaria.responses.MethodNotAllowed):
            request_parser.parse_request({'REQUEST_METHOD': 'DELETE'})


test_suite = unittest.TestLoader().loadTestsFromTestCase(TestRequestParser)
test_suite.addTest(doctest.DocTestSuite(confeitaria.server.requestparser))

def load_tests(loader, tests, ignore):
    return test_suite

if __name__ == "__main__":
    unittest.main()
