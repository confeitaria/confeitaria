import unittest

import inelegant.finder

import server
import requestparser
import environment
import session

load_tests = inelegant.finder.TestFinder(
    server, requestparser, environment, session
).load_tests

if __name__ == "__main__":
    unittest.main()
