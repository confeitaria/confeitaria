import unittest

import confeitaria.server.tests
import confeitaria.interfaces.tests
import confeitaria.responses.tests
import confeitaria.server.tests

modules = (
    confeitaria.interfaces.tests,
    confeitaria.responses.tests,
    confeitaria.server.tests
)

test_suite = unittest.TestSuite()

for module in modules:
    test_suite.addTest(module.test_suite)

def load_tests(loader, tests, ignore):
    tests.addTest(test_suite)

    return tests
