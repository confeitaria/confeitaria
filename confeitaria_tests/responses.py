import unittest

import inelegant.finder

import confeitaria.responses.responses as responses

load_tests = inelegant.finder.TestFinder(__name__, responses).load_tests

if __name__ == "__main__":
    unittest.main()
