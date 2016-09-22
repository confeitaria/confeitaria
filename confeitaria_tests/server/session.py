#!/usr/bin/env python
#
# Copyright 2015 Adam Victor Brandizzi
#
# This file is part of Confeitaria.
#
# Confeitaria is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# Confeitaria is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Confeitaria.  If not, see <http://www.gnu.org/licenses/>.
import unittest

import inelegant.finder

import Cookie
import time

import confeitaria.server.session
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
        should be retrievable later.
        """
        storage = SessionStorage()
        session1 = storage['key']
        session1['value'] = 'example'

        session2 = storage['key']
        self.assertEquals('example', session2['value'])

    def test_expires(self):
        """
        The session storage should discard sessions after a specified interval.
        """
        storage = SessionStorage(timeout=0.001)
        session1 = storage['key']
        session1['value'] = 'example'
        session2 = storage['key']
        self.assertEquals('example', session2['value'])

        time.sleep(0.001)

        session3 = storage['key']
        self.assertNotIn('value', session3)


load_tests = inelegant.finder.TestFinder(
    __name__, confeitaria.server.session
).load_tests

if __name__ == "__main__":
    unittest.main()
