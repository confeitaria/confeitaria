import doctest
import unittest

import confeitaria


def load_tests(loader, tests, ignore):
    tests.addTest(doctest.DocTestSuite(confeitaria.server.server))
    tests.addTest(doctest.DocTestSuite(confeitaria.runner))
    tests.addTest(
        doctest.DocFileSuite(
            'doc/index.rst', module_relative=True, package=confeitaria
        )
    )

    return tests

