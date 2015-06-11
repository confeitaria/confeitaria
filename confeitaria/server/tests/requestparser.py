import unittest
import doctest

import requests

from ..requestparser import RequestParser
from confeitaria.responses import NotFound

import confeitaria.server.requestparser

class TestRequestParser(unittest.TestCase):

    def test_get_root(self):
        """
        This test ensures that the root path (``/``) is mapped to the root page.
        """
        class TestPage(object):
            def index(self):
                return ''

        page = TestPage()
        request_parser = RequestParser(page)
        request = request_parser.parse_request('/')
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
            request_parser.parse_request('/nosub')

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
            request_parser.parse_request('/nosub')

    def test_path_args(self):
        """
        This test ensures that the parser can find parameters in path.
        """
        class TestPage(object):
            def index(self, arg):
                return ''

        page = TestPage()
        request_parser = RequestParser(page)
        request = request_parser.parse_request('/value')

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
            request_parser.parse_request('/')

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
        request = request_parser.parse_request('/value')

        self.assertEquals(page, request.page)
        self.assertEquals(['value'], request.path_args)
        self.assertEquals(['value'], request.args)

        with self.assertRaises(NotFound):
            request_parser.parse_request('/value/excess')


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
        request = request_parser.parse_request('/?kwarg2=value')

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
        request = request_parser.parse_request('/?kwarg=value&arg=no')

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
        request = request_parser.parse_request('/example?kwarg=value&arg=no')

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
        request = request_parser.parse_request('/value1/value2?kwarg2=value')

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

        request = request_parser.parse_request('/value')

        self.assertEquals(page, request.page)
        self.assertEquals(['value'], request.args)
        self.assertEquals(
            'page: root, arg: value',
            request.page.index(*request.args, **request.kwargs)
        )

        request = request_parser.parse_request('/attribute')

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

        request = request_parser.parse_request('/sub', '')

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

        request = request_parser.parse_request('/sub', 'kwarg=example')

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
        request = request_parser.parse_request('/?kwarg=value&kwarg1=example')

        self.assertEquals(
            {'kwarg': 'value', 'kwarg1': 'example'}, request.query_args
        )

    def test_request_not_tuple_anymore(self):
        """ In the past, the request object used to be a tuple. It proved to
        be hard to maintain and confusing. As a consequence, we removed this
        behavior from it. This test registers this change.
        """
        class TestPage(object):
            def index(self):
                return ''

        page = TestPage()
        request_parser = RequestParser(page)

        with self.assertRaises(TypeError):
            _, _, _ = request_parser.parse_request('')


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

        request = request_parser.parse_request('/')
        self.assertEquals('/', request.url)

        request = request_parser.parse_request('/?arg=1')
        self.assertEquals('/?arg=1', request.url)

        request = request_parser.parse_request('/sub')
        self.assertEquals('/sub', request.url)

test_suite = unittest.TestLoader().loadTestsFromTestCase(TestRequestParser)
test_suite.addTest(doctest.DocTestSuite(confeitaria.server.requestparser))

def load_tests(loader, tests, ignore):
    return test_suite

if __name__ == "__main__":
    unittest.main()
