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

import server
import requestparser
import environment
import session

load_tests = inelegant.finder.TestFinder(
    server, requestparser, environment, session
).load_tests

if __name__ == "__main__":
    unittest.main()
