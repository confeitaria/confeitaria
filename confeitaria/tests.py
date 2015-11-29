import unittest

import inelegant.finder

import confeitaria.server.tests
import confeitaria.interfaces.tests
import confeitaria.responses.tests
import confeitaria.server.tests

load_tests = inelegant.finder.TestFinder(
    'doc/index.rst',
    confeitaria.interfaces.tests,
    confeitaria.responses.tests,
    confeitaria.server.tests
).load_tests

if __name__ == "__main__":
    unittest.main()
