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

test_suite = unittest.TestLoader().loadTestsFromTestCase(TestURLedPage)
test_suite.addTest(doctest.DocTestSuite(interfaces))

def load_tests(loader, tests, ignore):
    tests.addTest(test_suite)

    return tests
