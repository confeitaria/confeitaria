import unittest

import requests

from ..urlparser import ObjectPublisherURLParser, HTTP404NotFound

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

        with self.assertRaises(HTTP404NotFound):
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

        with self.assertRaises(HTTP404NotFound):
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

        with self.assertRaises(HTTP404NotFound):
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

if __name__ == "__main__":
    unittest.main()
