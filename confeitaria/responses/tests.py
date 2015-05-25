import doctest
import unittest

import responses

test_suite = unittest.TestSuite()
test_suite.addTest(doctest.DocTestSuite(responses))

def load_tests(loader, tests, ignore):
    return test_suite
