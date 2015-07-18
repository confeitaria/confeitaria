import unittest
import doctest

try:
    import cStringIO as StringIO
except:
    import StringIO

import requests

from confeitaria.responses import NotFound

import confeitaria.server.requestparser
from confeitaria.server.requestparser import \
    RequestParser, subdict, path_dict, first_prefix, signature

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

class TestRequestParserFunctions(unittest.TestCase):

    def test_subdict(self):
        """
        ``subdict()`` receives a dict and a list of strings and return a dict
        containing all values mapped by the list of strings if present in the
        original dict.
        """
        self.assertEquals({'a': 1}, subdict({'a': 1, 'b': 2}, ['a']))

    def test_subdict_ignores_unavailable_values(self):
        """
        ``subdict()`  just ignores and key not found in the dict.
        """
        self.assertEquals({'a': 1}, subdict({'a': 1, 'b': 2}, ['a', 'c']))

    def test_path_dict(self):
        """
        ``path_dict()`` receives an object as its argument and returns a dict
        whose keys are the "path" to each attribute of the object (recursively)
        and the values are the attributes. Only objects satisfying a given
        condition will be added to the dict
        """
        class Obj(object):
            pass

        o = Obj()
        o.sub = Obj()
        o.sub.another = Obj()
        o.sub.value = 'a'
        o.sub.another.value = 3
        o.another = Obj()
        o.another.value = 3.14

        pd = path_dict(o, lambda o: isinstance(o, Obj))

        self.assertEquals(pd[''], o)
        self.assertEquals(pd['sub'], o.sub)
        self.assertEquals(pd['sub.another'], o.sub.another)
        self.assertEquals(pd['another'], o.another)

    def test_path_dict_with_sep(self):
        """
        You should be able to define the separator fo ``path_dict()``.
        condition will be added to the dict
        """
        class Obj(object):
            pass

        o = Obj()
        o.sub = Obj()
        o.sub.another = Obj()
        o.sub.value = 'a'
        o.sub.another.value = 3
        o.another = Obj()
        o.another.value = 3.14

        pd = path_dict(o, lambda o: isinstance(o, Obj), sep='/')

        self.assertEquals(pd[''], o)
        self.assertEquals(pd['sub'], o.sub)
        self.assertEquals(pd['sub/another'], o.sub.another)
        self.assertEquals(pd['another'], o.another)

    def test_path_dict_with_path(self):
        """
        If you give a path to``path_dict()`` it will preceed all other ones.
        """
        class Obj(object):
            pass

        o = Obj()
        o.sub = Obj()
        o.sub.another = Obj()
        o.sub.value = 'a'
        o.sub.another.value = 3
        o.another = Obj()
        o.another.value = 3.14

        pd = path_dict(o, lambda o: isinstance(o, Obj), path='o')

        self.assertEquals(pd['o'], o)
        self.assertEquals(pd['o.sub'], o.sub)
        self.assertEquals(pd['o.sub.another'], o.sub.another)
        self.assertEquals(pd['o.another'], o.another)

    def test_first_prefix(self):
        """
        Given a list of strings ``l`` and a string ``s``, ``first_prefix()``
        finds the first item from ``l`` that is a prefix for ``s`` (i.e. the
        item ``i`` from ``l`` that satisfies ``s.startswith(i)``.
        """
        self.assertEquals('a', first_prefix('abc', ['b', 'a', 'abc']))

    def test_first_prefix_none(self):
        """
        If ``first_prefix()`` finds no prefix from the list, it returns ``None``
        except if the ``default`` parameter is given.
        """
        self.assertEquals(None, first_prefix('jkl', ['b', 'a', 'abc']))
        self.assertEquals(
            'J', first_prefix('jkl', ['b', 'a', 'abc'], default='J')
        )

    def test_signature(self):
        """
        ``signature()`` should return a named tuple representing the argspec of
        the function in a more palatable way.
        """
        def f(a, b, c=3, d=3.14, e=4, *args, **kwargs): pass
        sig = signature(f)

        self.assertEquals(['a', 'b'], sig.args)
        self.assertEquals({'c': 3, 'd': 3.14, 'e': 4}, sig.kwargs)
        self.assertEquals('args', sig.varargs)
        self.assertEquals('kwargs', sig.keywords)

    def test_signature_bound_method(self):
        """
        ``signature()`` should work with bound methods.
        """
        class O(object):
            def f(self, a, b, c=3, e=4, *args, **kwargs): pass
        sig = signature(O().f)

        self.assertEquals(['self', 'a', 'b'], sig.args)
        self.assertEquals({'c': 3, 'e': 4}, sig.kwargs)
        self.assertEquals('args', sig.varargs)
        self.assertEquals('kwargs', sig.keywords)

    def test_signature_bound_method_exclude_self_bound_method(self):
        """
        ``signature()`` should not list the first ("self") argument from a bound
        method if called with ``exclude_self=True``.
        """
        class O(object):
            def f(self, a, b, c=3, e=4, *args, **kwargs): pass
        sig = signature(O().f, exclude_self=True)

        self.assertEquals(['a', 'b'], sig.args)
        self.assertEquals({'c': 3, 'e': 4}, sig.kwargs)
        self.assertEquals('args', sig.varargs)
        self.assertEquals('kwargs', sig.keywords)

    def test_signature_bound_method_exclude_self_unbound_method(self):
        """
        ``signature()`` should list the first ("self") argument from a unbound
        method if called with ``exclude_self=True``.
        """
        class O(object):
            def f(self, a, b, c=3, e=4, *args, **kwargs): pass
        sig = signature(O.f, exclude_self=True)

        self.assertEquals(['self', 'a', 'b'], sig.args)
        self.assertEquals({'c': 3, 'e': 4}, sig.kwargs)
        self.assertEquals('args', sig.varargs)
        self.assertEquals('kwargs', sig.keywords)

    def test_signature_bound_method_exclude_self_functio(self):
        """
        ``signature()`` should list the first ("self") argument from a function
        if called with ``exclude_self=True``.
        """
        def f(s, a, b, c=3, e=4, *args, **kwargs): pass
        sig = signature(f, exclude_self=True)

        self.assertEquals(['s', 'a', 'b'], sig.args)
        self.assertEquals({'c': 3, 'e': 4}, sig.kwargs)
        self.assertEquals('args', sig.varargs)
        self.assertEquals('kwargs', sig.keywords)

    def test_signature_no_arg(self):
        """
        ``signature()`` should work with functions without args.
        """
        def f(): pass
        sig = signature(f)

        self.assertEquals([], sig.args)
        self.assertEquals({}, sig.kwargs)
        self.assertEquals(None, sig.varargs)
        self.assertEquals(None, sig.keywords)

    def test_signature_callable(self):
        """
        ``signature()`` should work with callables.
        """
        class F(object):
            def __call__(self, a, b, c=3, e=4, *args, **kwargs): pass
        sig = signature(F())

        self.assertEquals(['self', 'a', 'b'], sig.args)
        self.assertEquals({'c': 3, 'e': 4}, sig.kwargs)
        self.assertEquals('args', sig.varargs)
        self.assertEquals('kwargs', sig.keywords)

test_suite = unittest.TestLoader().loadTestsFromTestCase(TestRequestParser)
test_suite.addTest(
    unittest.TestLoader().loadTestsFromTestCase(TestRequestParserFunctions)
)
test_suite.addTest(doctest.DocTestSuite(confeitaria.server.requestparser))

def load_tests(loader, tests, ignore):
    return test_suite

if __name__ == "__main__":
    unittest.main()
