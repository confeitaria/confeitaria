import unittest
import doctest
try:
    import cStringIO as StringIO
except:
    import StringIO


import confeitaria.server.environment
from confeitaria.server.environment import Environment, parse_qs_flat

class TestEnvironment(unittest.TestCase):

    def test_no_arg(self):
        """
        ``Environment`` can be created without any arguments, which will yield
        only default values.
        """
        env = Environment()

        self.assertEquals('GET', env.request_method)
        self.assertEquals('', env.path_info)
        self.assertEquals('', env.query_string)
        self.assertEquals({}, env.query_args)
        self.assertEquals('', env.url)
        self.assertEquals('', env.request_body)
        self.assertEquals({}, env.form_args)
        self.assertEquals('', env.http_cookie.output())

    def test_empty_dict(self):
        """
        The first arg for the ``Environment`` constructor is an environment
        dict. If this dict is empty, the result is equivalent to call the
        constructor withouth arguments.
        """
        env = Environment({})

        self.assertEquals('GET', env.request_method)
        self.assertEquals('', env.path_info)
        self.assertEquals('', env.query_string)
        self.assertEquals({}, env.query_args)
        self.assertEquals('', env.url)
        self.assertEquals('', env.request_body)
        self.assertEquals({}, env.form_args)
        self.assertEquals('', env.http_cookie.output())

    def test_request_method(self):
        """
        The environment should have the request method from the environment
        dict.
        """
        env = Environment({'REQUEST_METHOD': 'POST'})
        self.assertEquals('POST', env.request_method)

        env = Environment({'REQUEST_METHOD': 'GET'})
        self.assertEquals('GET', env.request_method)

    def test_path_info(self):
        """
        The environment should have the path info from the environment dict.
        """
        env = Environment({'PATH_INFO': '/example/value'})
        self.assertEquals('/example/value', env.path_info)

    def test_query_string(self):
        """
        The environment should have the query_string from the environment dict.
        It should also have it as a dictionary
        """
        env = Environment({'QUERY_STRING': 'a=b&c=d'})
        self.assertEquals('a=b&c=d', env.query_string)
        self.assertEquals({'a': 'b', 'c': 'd'}, env.query_args)

    def test_url(self):
        """
        The envirionment should have a full URL to be used for parsing.
        """
        env = Environment(
            {'PATH_INFO': '/example/value', 'QUERY_STRING': 'a=b&c=d'}
        )
        self.assertEquals('/example/value?a=b&c=d', env.url)


    def test_request_body(self):
        """
        If the request has a body, then it should be read into the
        ``request_body`` attribute and be parsed as well into a dict at
        ``form_args``.
        """
        content = 'a=b&c=d'
        env = Environment(
            {
                'CONTENT_LENGTH': len(content),
                'wsgi.input': StringIO.StringIO(content)
            }
        )
        self.assertEquals('a=b&c=d', env.request_body)
        self.assertEquals({'a': 'b', 'c': 'd'}, env.form_args)

    def test_http_cookie(self):
        """
        The environment should have cookies, already as ``Cookie.SimpleCookie``
        instance.
        """
        env = Environment({'HTTP_COOKIE': 'a=b'})
        self.assertEquals('Set-Cookie: a=b', env.http_cookie.output())

class TestEnvironmentFunctions(unittest.TestCase):


    def test_parse_qs_flat(self):
        """
        ``parse_qs_flat()`` works very much like ``urlparse.parse_qs()`` with a
        difference: while the values of the ``urlparse.parse_qs()`` dict are
        lists, in ``parse_qs_flat()`` they are lists only if more than one is
        given; otherwise, the sole value is the dict value.
        """
        self.assertEquals(
            {'a': '1', 'b': ['2', '3']}, parse_qs_flat('a=1&b=2&b=3')
        )

test_suite = unittest.TestLoader().loadTestsFromTestCase(TestEnvironment)
test_suite = unittest.TestLoader().loadTestsFromTestCase(
    TestEnvironmentFunctions
)
test_suite.addTest(doctest.DocTestSuite(confeitaria.server.environment))

def load_tests(loader, tests, ignore):
    return test_suite

if __name__ == "__main__":
    unittest.main()
