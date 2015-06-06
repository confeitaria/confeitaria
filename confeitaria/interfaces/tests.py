import doctest
import unittest

import interfaces

class TestIsPage(unittest.TestCase):

    def test_is_page_true_index_method(self):
        """
        ``is_page()`` should return ``True`` if its argument has an ``index()``
        bound method.
        """
        class TestPage(object):
            def index(self):
                return ''

        self.assertTrue(interfaces.is_page(TestPage()))

    def test_is_page_true_action_method(self):
        """
        ``is_page()`` should return ``True`` if its argument has an ``action()``
        bound method.
        """
        class TestPage(object):
            def action(self):
                return ''

        self.assertTrue(interfaces.is_page(TestPage()))

    def test_is_page_false_no_method(self):
        """
        ``is_page()`` should return ``True`` if its argument has neither
        ``index()`` nor an ``action()`` bound method.
        """
        class TestObject(object):
            pass

        self.assertFalse(interfaces.is_page(TestObject()))

class TestURLedPage(unittest.TestCase):

    def test_set_url_to_get_url(self):
        """
        This test ensures that what goes into ``URLedPage.set_url()`` is
        retrieved by ``URLedPage.get_url()``.
        """
        page = interfaces.URLedPage()
        page.set_url('/test')

        self.assertEqual('/test', page.get_url())

    def test_has_set_url(self):
        """
        This tests ensures the ``has_set_url()`` returns ``True`` if its
        argument has a ``set_url()`` method accepting one mandatory argument.
        """
        class TestPage(object):
            def set_url(self, value):
                pass

        self.assertTrue(interfaces.has_set_url(TestPage()))

class TestCookiedPage(unittest.TestCase):

    def test_set_cookies_to_get_gookies(self):
        """
        This test ensures that what goes into ``CookiedPage.set_cookies()`` is
        retrieved by ``CookiedPage.get_cookies()``.
        """
        import Cookie
        page = interfaces.CookiedPage()
        cookies = Cookie.SimpleCookie()
        cookies['example'] = 'value'
        page.set_cookies(cookies)

        self.assertEqual(cookies['example'], page.get_cookies()['example'])

    def test_has_set_cookies(self):
        """
        This tests ensures the ``has_set_cookies()`` returns ``True`` if its
        argument has a ``set_cookies()`` method accepting one mandatory
        argument.
        """
        class TestPage(object):
            def set_cookies(self, value):
                pass

        self.assertTrue(interfaces.has_set_cookies(TestPage()))

class TestSessionedPage(unittest.TestCase):

    def test_set_session_to_get_session(self):
        """
        This test ensures that what goes into ``SessionedPage.set_session()`` is
        retrieved by ``SessionedPage.get_session()``.
        """
        page = interfaces.SessionedPage()
        page.set_session({'value': 'example'})

        self.assertEqual({'value': 'example'}, page.get_session())

    def test_has_set_session(self):
        """
        This tests ensures the ``has_set_session()`` returns ``True`` if its
        argument has a ``set_session()`` method accepting one mandatory
        argument.
        """
        class TestPage(object):
            def set_session(self, value):
                pass

        self.assertTrue(interfaces.has_set_session(TestPage()))

class TestRequestedPage(unittest.TestCase):

    def test_set_request_to_get_request(self):
        """
        This test ensures that what goes into ``RequestedPage.set_request()`` is
        retrieved by ``RequestedPage.get_request()``.
        """
        import confeitaria.request

        page = interfaces.RequestedPage()
        request = confeitaria.request.Request(
            args=['arg1', 'arg2'], kwargs={'value': 'example'}
        )
        page.set_request(request)

        self.assertEqual(['arg1', 'arg2'], page.get_request().args)
        self.assertEqual({'value': 'example'}, page.get_request().kwargs)

    def test_has_set_request(self):
        """
        This tests ensures the ``has_set_request()`` returns ``True`` if its
        argument has a ``set_request()`` method accepting one mandatory
        argument.
        """
        class TestPage(object):
            def set_request(self, value):
                pass

        self.assertTrue(interfaces.has_set_request(TestPage()))

class TestHasSetter(unittest.TestCase):

    def test_has_setter_is_false_no_method(self):
        """
        This tests ensures the ``has_setter()`` returns ``False`` if the
        required attribute is no method.
        """
        class TestPage(object):
            def __init__(self):
                self.set_example = 'string'

        self.assertFalse(interfaces.has_setter(TestPage(), 'example'))

    def test_has_setter_is_false_no_argument(self):
        """
        This tests ensures the ``has_setter()`` returns ``False`` if its
        argument has the expected method but it receives no arguments.
        """
        class TestPage(object):
            def set_example(self):
                pass

        self.assertFalse(interfaces.has_setter(TestPage(), 'example'))

    def test_has_setter_is_false_more_than_one_mandatory_argument(self):
        """
        This tests ensures the ``has_setter()`` returns ``False`` if its
        argument has the expected method but it has more than one unbound
        mandatory argumet.
        """
        class TestPage(object):
            def set_example(self, value1, value2):
                pass

        self.assertFalse(interfaces.has_setter(TestPage(), 'example'))

    def test_has_setter_is_true_optional_argumets(self):
        """
        This tests ensures the ``has_setter()`` returns ``True`` if its
        argument has the expected method method with one mandatory argument and
        some optional ones.
        """
        class TestPage(object):
            def set_example(self, value1, value2=None, *args, **kwargs):
                pass

        self.assertTrue(interfaces.has_setter(TestPage(), 'example'))

    def test_has_setter_is_false_to_unbound_method(self):
        """
        This tests ensures the ``has_setter()`` returns ``False`` if its
        argument the expected method but it is not bound. (For example,
        it is a page class.)
        """
        class TestPage(object):
            def set_example(self, value):
                pass

        self.assertFalse(interfaces.has_setter(TestPage, 'example'))

test_suite = unittest.TestSuite()
test_suite.addTest(
    unittest.defaultTestLoader.loadTestsFromTestCase(TestURLedPage))
test_suite.addTest(
    unittest.defaultTestLoader.loadTestsFromTestCase(TestCookiedPage))
test_suite.addTest(
    unittest.defaultTestLoader.loadTestsFromTestCase(TestSessionedPage))
test_suite.addTest(
    unittest.defaultTestLoader.loadTestsFromTestCase(TestRequestedPage))
test_suite.addTest(
    unittest.defaultTestLoader.loadTestsFromTestCase(TestIsPage))
test_suite.addTest(
    unittest.defaultTestLoader.loadTestsFromTestCase(TestHasSetter))
test_suite.addTest(doctest.DocTestSuite(interfaces))

def load_tests(loader, tests, ignore):
    return test_suite
