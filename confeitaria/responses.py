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
Responses are exceptions that, when raised, can force the server to send a
specific response with a status code and some headers.
"""


class Response(Exception):
    """
    Superclass exception for representing HTTP responses. This exception (and
    its subclasses) can be raised to return a specific HTTP response to the
    browser.

    It expects to receive as a parameter at least a status code and the headers
    to be sent.

    ::

        >>> r = Response('404 Not Found')
        >>> r.status_code
        '404 Not Found'

    It can also receive a list containing the headers::

        >>> r = Response(
        ...     '302 Found', headers=[('Location', 'http://pudim.com.br')]
        ... )
        >>> r.status_code
        '302 Found'
        >>> r.headers
        [('Location', 'http://pudim.com.br')]

    For commodity, the list can be given as a dictionary (obviously, only if
    there is no repeated header)::

        >>> r = Response(
        ...     '302 Found', headers={'Location': 'http://pudim.com.br'}
        ... )
        >>> r.status_code
        '302 Found'
        >>> r.headers
        [('Location', 'http://pudim.com.br')]
    """

    def __init__(self, status_code, message=None, headers=None, *args):
        Exception.__init__(self, message, *args)

        self.status_code = status_code

        try:
            self.headers = headers.items()
        except AttributeError:
            self.headers = [] if headers is None else headers


class OK(Response):
    """
    This response reports that the request was successful::

        >>> r = OK(message='Just fine')
        >>> r.status_code
        '200 OK'
        >>> r.message
        'Just fine'
    """

    def __init__(self, message='', headers=None, *args):
        headers = [] if not headers else headers
        Response.__init__(self, '200 OK', message, headers, *args)


class MovedPermanently(Response):
    """
    This response redirects the client to a new URL, to which the sought
    content was supposedly moved::

        >>> r = MovedPermanently(location='http://pudim.com.br')
        >>> r.status_code
        '301 Moved Permanently'
        >>> r.headers
        [('Location', 'http://pudim.com.br')]
    """

    status_code = '301 Moved Permanently'

    def __init__(self, location=None, message=None, headers=None, *args):
        headers = [] if not headers else headers
        headers.append(('Location', location))
        Response.__init__(
            self, MovedPermanently.status_code, message, headers, *args)
        self.location = location


class SeeOther(Response):
    """
    This response redirects the client to a new URL, where a representation of
    the requested URL can be found::

        >>> r = SeeOther(location='http://pudim.com.br')
        >>> r.status_code
        '303 See Other'
        >>> r.headers
        [('Location', 'http://pudim.com.br')]
    """

    status_code = '303 See Other'

    def __init__(self, location=None, message=None, headers=None, *args):
        headers = [] if not headers else headers
        headers.append(('Location', location))
        Response.__init__(self, SeeOther.status_code, message, headers, *args)
        self.location = location


class NotFound(Response):
    """
    This response indicates the requested resource could not be found::

        >>> r = NotFound()
        >>> r.status_code
        '404 Not Found'
    """

    status_code = '404 Not Found'

    def __init__(self, message=None, headers=None, *args):
        Response.__init__(self, NotFound.status_code, message, headers, *args)


class MethodNotAllowed(Response):
    """
    This response indicates the requested resource is available but does not
    handle the requested HTTP method::

        >>> r = MethodNotAllowed()
        >>> r.status_code
        '405 Method Not Allowed'
    """

    status_code = '405 Method Not Allowed'

    def __init__(self, message=None, headers=None, *args):
        Response.__init__(
            self, MethodNotAllowed.status_code, message, headers, *args)
