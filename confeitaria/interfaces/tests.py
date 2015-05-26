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
        This tests ensures the ``has_set_url()`` returns ``False`` if its
        argument has a ``set_url()`` method accepting one mandatory argument.
        """
        class TestPage(object):
            def set_url(self, value):
                pass

        self.assertTrue(interfaces.has_set_url(TestPage()))

    def test_has_set_url_is_false_no_method(self):
        """
        This tests ensures the ``has_set_url()`` returns ``False`` if its
        argument has a ``set_url`` attribute that is not a method.
        """
        class TestPage(object):
            def __init__(self):
                self.set_url = 'string'

        self.assertFalse(interfaces.has_set_url(TestPage()))

    def test_has_set_url_is_false_no_argument(self):
        """
        This tests ensures the ``has_set_url()`` returns ``False`` if its
        argument has a ``set_url()`` method accepting no argument.
        """
        class TestPage(object):
            def set_url(self):
                pass

        self.assertFalse(interfaces.has_set_url(TestPage()))

    def test_has_set_url_is_false_more_than_one_argument(self):
        """
        This tests ensures the ``has_set_url()`` returns ``False`` if its
        argument has a ``set_url()`` method with more than one required
        argument.
        """
        class TestPage(object):
            def set_url(self, value1, value2):
                pass

        self.assertFalse(interfaces.has_set_url(TestPage()))

    def test_has_set_url_is_true_optional_argumets(self):
        """
        This tests ensures the ``has_set_url()`` returns ``True`` if its
        argument has a ``set_url()`` method with one mandatory argument and
        some optional ones.
        """
        class TestPage(object):
            def set_url(self, value1, value2=None, *args, **kwargs):
                pass

        self.assertTrue(interfaces.has_set_url(TestPage()))

test_suite = unittest.TestSuite()
test_suite.addTest(
    unittest.defaultTestLoader.loadTestsFromTestCase(TestURLedPage))
test_suite.addTest(
    unittest.defaultTestLoader.loadTestsFromTestCase(TestIsPage))
test_suite.addTest(doctest.DocTestSuite(interfaces))

def load_tests(loader, tests, ignore):
    return test_suite
