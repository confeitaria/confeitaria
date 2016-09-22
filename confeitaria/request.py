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
"""
A request object should contain the info relevant about the HTTP request.
"""


class Request(object):

    def __init__(
            self, page=None, path_args=None, query_args=None, form_args=None,
            args=None, kwargs=None, url=None, method=None):
        self.page = page
        self.path_args = path_args if path_args is not None else []
        self.query_args = query_args if query_args is not None else {}
        self.form_args = form_args if form_args is not None else {}
        self.args = args if args is not None else []
        self.kwargs = kwargs if kwargs is not None else {}
        self.url = url
        self.method = method
