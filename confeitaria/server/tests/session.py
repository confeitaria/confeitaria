import unittest
import doctest

import Cookie

from confeitaria.server.session import SessionStorage

class TestSessionStorage(unittest.TestCase):

    def test_get_key_not_defined_yet(self):
        """
        The session storage should return a new dict when a non-existent key is
        requested.
        """
        storage = SessionStorage()

        self.assertNotIn('key1', storage)
        s1 = storage['key1']
        self.assertIn('key1', storage)

        self.assertNotIn('key2', storage)
        s2 = storage['key2']
        self.assertIn('key2', storage)

        self.assertIsNot(s1, s2)

    def test_status_persisted(self):
        """
        If someting is set into one of the sessions from session storage, it
        should be retrievable later..
        """
        storage = SessionStorage()
        session1 = storage['key']
        session1['value'] = 'example'

        session2 = storage['key']
        self.assertEquals('example', session2['value'])


test_suite = unittest.TestLoader().loadTestsFromTestCase(TestSessionStorage)

def load_tests(loader, tests, ignore):
    return test_suite

if __name__ == "__main__":
    unittest.main()
