import unittest

import inelegant.finder

import confeitaria_tests.server
import confeitaria_tests.interfaces
import confeitaria_tests.responses

load_tests = inelegant.finder.TestFinder(
    '../doc/index.rst',
    confeitaria_tests.interfaces,
    confeitaria_tests.responses,
    confeitaria_tests.server
).load_tests

if __name__ == "__main__":
    unittest.main()
