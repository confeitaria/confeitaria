import unittest
import responses

import inelegant.finder

load_tests = inelegant.finder.TestFinder(__name__, responses).load_tests

if __name__ == "__main__":
    unittest.main()
