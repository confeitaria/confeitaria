import doctest
import unittest

import interfaces

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



test_suite = unittest.TestLoader().loadTestsFromTestCase(TestURLedPage)
test_suite.addTest(doctest.DocTestSuite(interfaces))

def load_tests(loader, tests, ignore):
    return test_suite
