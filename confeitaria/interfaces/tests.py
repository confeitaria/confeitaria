import doctest
import unittest

import interfaces

test_suite = unittest.TestSuite()
test_suite.addTest(doctest.DocTestSuite(interfaces))

def load_tests(loader, tests, ignore):
    tests.addTest(test_suite)

    return tests
