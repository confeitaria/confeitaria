import unittest

import requests

from ..urlparser import ObjectPublisherURLParser
from confeitaria.responses import NotFound

class TestObjectPublisherURLParser(unittest.TestCase):

    def test_get_root(self):
        """
        This test ensures that the root path (``/``) is mapped to the root page.
        """
        class TestPage(object):
            def index(self):
                return ''

        root_page = TestPage()
        url_parser = ObjectPublisherURLParser(root_page)
        page, args, kwargs = url_parser.parse_url('/')
        self.assertEquals(root_page, page)
        self.assertEquals([], args)
        self.assertEquals({}, kwargs)

    def test_subpage_not_found_404(self):
        """
        This test ensures that, if a non-existence page is requested, an
        exception reporting a 404 Not Found status is raised.
        """
        class TestPage(object):
            def index(self):
                return ''

        page = TestPage()
        url_parser = ObjectPublisherURLParser(page)

        with self.assertRaises(NotFound):
            url_parser.parse_url('/nosub')

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
        url_parser = ObjectPublisherURLParser(page)

        with self.assertRaises(NotFound):
            url_parser.parse_url('/nosub')

    def test_path_parameters(self):
        """
        This test ensures that the parser can find parameters in path.
        """
        class TestPage(object):
            def index(self, arg):
                return ''

        page = TestPage()
        url_parser = ObjectPublisherURLParser(page)
        p, args, kwargs = url_parser.parse_url('/value')

        self.assertEquals(page, p)
        self.assertEquals(['value'], args)
        self.assertEquals({}, kwargs)

    def test_missing_path_parameters_are_none(self):
        """
        This test ensures that  parser finds a page whose index method
        expects arguments, but the parameters are not passed in the path,
        the the arguments values will be ``None``.
        """
        class TestPage(object):
            def index(self, arg):
                return ''

        page = TestPage()
        url_parser = ObjectPublisherURLParser(page)
        p, args, kwargs = url_parser.parse_url('/')

        self.assertEquals(page, p)
        self.assertEquals([None], args)
        self.assertEquals({}, kwargs)

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
        url_parser = ObjectPublisherURLParser(page)
        p, args, kwargs = url_parser.parse_url('/value')

        self.assertEquals(page, p)
        self.assertEquals(['value'], args)
        self.assertEquals({}, kwargs)

        with self.assertRaises(NotFound):
            _, _, _ = url_parser.parse_url('/value/excess')


    def test_query_parameters(self):
        """
        This test ensures that when parser finds a page whose index method
        expects arguments, but the number of parameters in the path is larger
        than the number of arguments in the index method, then a 404 Not Found
        response will follow

        """
        class TestPage(object):
            def index(self, kwarg1=None, kwarg2=None):
                return ''

        page = TestPage()
        url_parser = ObjectPublisherURLParser(page)
        p, args, kwargs = url_parser.parse_url('/?kwarg2=value')

        self.assertEquals(page, p)
        self.assertEquals([], args)
        self.assertEquals({'kwarg1': None, 'kwarg2': 'value'}, kwargs)

    def test_path_and_query_parameters(self):
        """
        This test ensures that when parser finds a page whose index method
        expects arguments, but the number of parameters in the path is larger
        than the number of arguments in the index method, then a 404 Not Found
        response will follow

        """
        class TestPage(object):
            def index(self, arg1, arg2, kwarg1=None, kwarg2=None):
                return ''

        page = TestPage()
        url_parser = ObjectPublisherURLParser(page)
        p, args, kwargs = url_parser.parse_url('/value1?kwarg2=kwvalue2')

        self.assertEquals(page, p)
        self.assertEquals(['value1', None], args)
        self.assertEquals({'kwarg1': None, 'kwarg2': 'kwvalue2'}, kwargs)

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
        url_parser = ObjectPublisherURLParser(page)

        p, args, kwargs = url_parser.parse_url('/value')

        self.assertEquals(page, p)
        self.assertEquals(['value'], args)
        self.assertEquals({}, kwargs)
        self.assertEquals('page: root, arg: value', p.index(*args, **kwargs))

        p, args, kwargs = url_parser.parse_url('/attribute')

        self.assertEquals(page.attribute, p)
        self.assertEquals([], args)
        self.assertEquals({}, kwargs)
        self.assertEquals('page: attribute', p.index(*args, **kwargs))

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
        url_parser = ObjectPublisherURLParser(page)

        p, args, kwargs = url_parser.parse_url('/sub', '')

        self.assertEquals(p, page.sub)

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
        url_parser = ObjectPublisherURLParser(page)

        p, args, kwargs = url_parser.parse_url('/sub', 'kwarg=example')

        self.assertEquals({'kwarg': 'example'}, kwargs)

    def test_returned_tuple_is_request_object(self):
        """
        The tuple returned by the parser should also be a request object.
        """
        class TestPage(object):
            def index(self, kwarg=None):
                return ''

        page = TestPage()
        url_parser = ObjectPublisherURLParser(page)
        request = url_parser.parse_url('/?kwarg=value&kwarg1=example')

        self.assertEquals(
            {'kwarg': 'value', 'kwarg1': 'example'}, request.query_parameters
        )

if __name__ == "__main__":
    unittest.main()
