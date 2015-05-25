import doctest
import unittest

import responses

test_suite = unittest.TestSuite()
test_suite.addTest(doctest.DocTestSuite(responses))

def load_tests(loader, tests, ignore):
    tests.addTest(test_suite)

    return tests
