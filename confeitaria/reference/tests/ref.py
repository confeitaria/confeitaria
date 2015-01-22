import unittest

import requests

class TestReference(unittest.TestCase):
    """
    This test case provides some tests for behaviors that any Confeitaria
    implementation is supposed to support. Implementations are supposed to
    extend this class; the extending test case can have its own test methods
    as well.

    Any sublcass of ``TestReference`` should implement the ``get_server()``
    method. This method should expect a page object as its argument, and return
    some object that respect the ``with`` protocol in a way that:

    * in the ``__enter__()`` method, an HTTP server is asynchronously started at
      port 8080, running the Confeitaria implementation being tested; and
    * in the ``__exit__()`` method, the HTTP server is stopped.
    """

    def test_attributes_as_subpages(self):
        """
        This test ensures that when a path is requested to Confeitaria it will
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

        with self.get_server(root):
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

        with self.get_server(TestPage()):
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

        with self.get_server(TestPage()):
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

        with self.get_server(TestPage()):
            r = requests.get('http://localhost:8080/first/second')
            self.assertEquals('arg1: first; arg2: second', r.text)

    def test_index_parameters_from_path_and_query_args(self):
        """
        This test ensures that positional parameters will  be get from query
        path and the optional ones will be get from the query string
        """
        class TestPage(object):
            def index(self, arg1, arg2, kwarg1=None, kwarg2=None):
                return 'arg1={0}; arg2={1}; kwarg1={2}; kwarg2={3}'.format(
                    arg1, arg2, kwarg1, kwarg2
                )

        with self.get_server(TestPage()):
            r = requests.get('http://localhost:8080/one/cake')
            self.assertEquals(
                'arg1=one; arg2=cake; kwarg1=None; kwarg2=None', r.text
            )
            r = requests.get(
                'http://localhost:8080/this/pie?kwarg2=tasty&kwarg1=is'
            )
            self.assertEquals(
                'arg1=this; arg2=pie; kwarg1=is; kwarg2=tasty', r.text
            )

    def test_page_with_set_url_knows_its_path(self):
        """
        This test ensures that a page which has a ``set_url()`` method, the
        method will be called passing the URL of the page. This way, the page
        can have access to its own URL.
        """
        class TestPage(object):
            def index(self):
                return 'url: {0}'.format(self.url)
            def set_url(self, url):
                self.url = url


        root = TestPage()
        root.sub = TestPage()
        root.sub.another = TestPage()

        with self.get_server(root):
            r = requests.get('http://localhost:8080/')
            self.assertEquals('url: /', r.text)
            r = requests.get('http://localhost:8080/sub')
            self.assertEquals('url: /sub', r.text)
            r = requests.get('http://localhost:8080/sub/another')
            self.assertEquals('url: /sub/another', r.text)

    def test_page_knows_subpages_path(self):
        """
        This test ensures that a page with supbages providing a compatible
        ``set_url()`` method will know its subpages URLs.
        """
        class RootPage(object):
            def __init__(self):
                self.sub = SubPage()
                self.sub.another = SubPage()
            def index(self):
                return 'self.sub url: {0}; self.sub.another url: {1}'.format(
                    self.sub.url, self.sub.another.url
                )

        class SubPage(object):
            def index(self):
                return ''
            def set_url(self, url):
                self.url = url

        with self.get_server(RootPage()):
            r = requests.get('http://localhost:8080/')
            self.assertEquals(
                'self.sub url: /sub; self.sub.another url: /sub/another', r.text
            )

    def test_index_parameters_should_have_none_value(self):
        """
        This test ensures that mandatory parameters from index will receive
        ``None`` as their values if no value is found in the path.
        """
        class TestPage(object):
            def index(self, arg):
                if arg is not None:
                    result = 'arg: {0}'.format(arg)
                else:
                    result = 'no arg'
                return result

        with self.get_server(TestPage()):
            r = requests.get('http://localhost:8080/')
            self.assertEquals('no arg', r.text)
            r = requests.get('http://localhost:8080/example')
            self.assertEquals('arg: example', r.text)

    def test_too_many_index_parameters_results_in_404(self):
        """
        This test ensures that a page reached with more positional parameters
        than its index method expect will return 404 error code. This is so
        because these parameters, being part of the path, are supposed to
        represent a specific entity. Having too many of them is equivalent of
        trying to reach a non-existent document.
        """
        class TestPage(object):
            def index(self, arg):
                return 'irrelevant content'

        with self.get_server(TestPage()):
            r = requests.get('http://localhost:8080/sub')
            self.assertEquals(200, r.status_code)
            r = requests.get('http://localhost:8080/sub/another')
            self.assertEquals(404, r.status_code)

    def test_post_method(self):
        """
        A Confeitaria page can have a method ``action()`` for handling POST
        requests. Its behavior should be somewhat similar to the ``index()``
        method when it comes to handling parameters. Yet, it is not supposed
        to return an HTML document. How a document will - or will not - be
        returned is a issue to be defined in other tests.
        """
        class TestPage(object):
            post_parameter = None
            def action(self, kwarg=None):
                TestPage.post_parameter = kwarg
            def index(self):
                return 'post_parameter: {0}'.format(TestPage.post_parameter)

        with self.get_server(TestPage()):
            requests.post(
                'http://localhost:8080/', data={'kwarg': 'example'}
            )
            r = requests.get('http://localhost:8080/')
            self.assertEquals('post_parameter: example', r.text)

    def test_raising_redirect_moved_permanently(self):
        """
        Raising the ``MovedPermanently`` exception should result in a redirect.
        """
        import confeitaria.responses

        class TestPage(object):
            def index(self):
                raise confeitaria.responses.MovedPermanently('/sub')

        page = TestPage()

        with self.get_server(page):
            r = requests.get('http://localhost:8080/', allow_redirects=False)
            self.assertEquals(301, r.status_code)
            self.assertEquals('/sub', r.headers['location'])


    def test_raising_redirect_see_other(self):
        """
        Raising the ``SeeOther`` exception should result in a redirect.
        """
        import confeitaria.responses

        class TestPage(object):
            def index(self):
                raise confeitaria.responses.SeeOther('/sub')

        page = TestPage()

        with self.get_server(page):
            r = requests.get('http://localhost:8080/', allow_redirects=False)
            self.assertEquals(303, r.status_code)
            self.assertEquals('/sub', r.headers['location'])

    def test_raising_redirect_see_other_from_action(self):
        """
        Raising the ``SeeOther`` exception should result in a redirect,
        specially from an action method.
        """
        import confeitaria.responses

        class TestPage(object):
            post_parameter = None
            def index(self):
                return 'post_parameter: {0}'.format(TestPage.post_parameter)
            def action(self, kwarg=None):
                TestPage.post_parameter = kwarg
                raise confeitaria.responses.SeeOther('/')

        with self.get_server(TestPage()):
            r = requests.post(
                'http://localhost:8080/', data={'kwarg': 'example'}
            )
            r = requests.get('http://localhost:8080/')
            self.assertEquals(200, r.status_code)
            self.assertEquals('post_parameter: example', r.text)

    def test_get_request(self):
        """
        If a page has a ``set_request()`` method expecting an argument, then
        it should be called with an request object. This request object should
        give access to request parameters.
        """
        class TestPage(object):
            def set_request(self, request):
                self.req = request
            def index(self):
                return 'param: {0}'.format(self.req.query_parameters['param'])

        with self.get_server(TestPage()):
            r = requests.get('http://localhost:8080/?param=example')
            self.assertEquals('param: example', r.text)

    def test_raising_redirect_see_other_no_location(self):
        """
        Raising ``SeeOther`` without location should result in a redirect to the
        requested URL.
        """
        import confeitaria.responses

        class TestPage(object):
            def index(self):
                raise confeitaria.responses.SeeOther()

        page = TestPage()
        page.sub = TestPage()

        with self.get_server(page):
            r = requests.get('http://localhost:8080/', allow_redirects=False)
            self.assertEquals(303, r.status_code)
            self.assertEquals('/', r.headers['location'])
            r = requests.get('http://localhost:8080/sub', allow_redirects=False)
            self.assertEquals(303, r.status_code)
            self.assertEquals('/sub', r.headers['location'])

    def test_raising_redirect_see_other_no_location_from_action(self):
        """
        Raising ``SeeOther`` without location should result in a redirect to the
        requested URL.
        """
        import confeitaria.responses

        class TestPage(object):
            def index(self):
                raise confeitaria.responses.SeeOther()
            def action(self):
                raise confeitaria.responses.SeeOther()

        page = TestPage()

        with self.get_server(page):
            r = requests.post(
                'http://localhost:8080/?a=b', allow_redirects=False
            )
            self.assertEquals(303, r.status_code)
            self.assertEquals('/?a=b', r.headers['location'])
