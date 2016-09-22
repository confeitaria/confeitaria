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
import confeitaria.runner


class BasicDocumentationPage(object):
    """
    This page reads the HTML file ``index.html`` and returns its content for
    the HTTP response.
    """
    def index(self):
        import pkgutil

        return pkgutil.get_data('confeitaria', 'doc/index.html')

confeitaria.runner.run(BasicDocumentationPage())
