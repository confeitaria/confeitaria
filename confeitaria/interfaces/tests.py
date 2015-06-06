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
    unittest.defaultTestLoader.loadTestsFromTestCase(TestIsPage))
test_suite.addTest(
    unittest.defaultTestLoader.loadTestsFromTestCase(TestHasSetter))
test_suite.addTest(doctest.DocTestSuite(interfaces))

def load_tests(loader, tests, ignore):
    return test_suite
