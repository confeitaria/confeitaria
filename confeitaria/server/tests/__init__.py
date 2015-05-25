import unittest

from .server import test_suite as server_test_suite
from .requestparser import test_suite as request_parser_test_suite

test_suite = unittest.TestSuite()
test_suite.addTest(server_test_suite)
test_suite.addTest(request_parser_test_suite)
