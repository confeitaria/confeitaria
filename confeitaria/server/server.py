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
import os
import binascii

import wsgiref.simple_server as simple_server
import Cookie

import confeitaria.request
import confeitaria.responses


from .requestparser import RequestParser
from .session import SessionStorage
from .environment import Environment


class Server(object):
    """
    The ``Server`` objects listen to HTTP requests and serve responses
    according to the page object returned values.
    """

    def __init__(
            self, page, port=8000, session_storage=None):

        self.request_parser = RequestParser(page)

        if session_storage is None:
            self.session_storage = SessionStorage()

        self.port = port
        self._process = None

    def run(self, force=True):
        """
        This method starts the server up serving the given page.
        A page is an object of a class as the one below:

        >>> class TestPage(object):
        ...     def index(self):
        ...         return "This is a test"

        To run it, just call `Server.run()`, as in:

        >>> s = Server(TestPage())

        >>> import multiprocessing, inelegant.net
        >>> p = multiprocessing.Process(target=s.run)
        >>> p.start()
        >>> inelegant.net.wait_server_up('', s.port)

        Then the server is supposed to serve the content provided by the page:

        >>> import requests
        >>> r = requests.get('http://localhost:8000/')
        >>> r.text
        u'This is a test'
        >>> r.status_code
        200
        >>> r.headers['content-type']
        'text/html'

        >>> p.terminate()

        You can also, mostly for testing purposes, start up a server through a
        ``with`` statement:

        >>> with Server(TestPage()):
        ...     r = requests.get("http://localhost:8000")
        ...     r.text
        u'This is a test'
        """
        while True:
            import socket

            try:
                httpd = simple_server.make_server('', self.port, self.respond)
                print "Serving on port 8000..."
                httpd.serve_forever()
            except socket.error:
                if not force:
                    raise

    def respond(self, env_dict, start_response):
        """
        This method responds to HTTP requests encoded as a WSGI environment. It
        is a WSGI application `as defined by PEP 0333`__ if bound, and so it
        receives two arguments: a dict representing a WSGI environment and a
        callable to start a response. So, if we have a function like this::

        >>> def dummy_start_response(*args):
        ...     global response
        ...     response = args

        ...and a class like this::

        >>> class TestPage(object):
        ...     def index(self, arg=None):
        ...         return arg if arg is not None else 'no argument'


        ...given to a server::

        >>> s = Server(TestPage())

        ...then calling ``Server.respond()`` should return the output from the
        page::

        >>> s.respond({}, dummy_start_response)
        ['no argument']
        >>> s.respond({'QUERY_STRING': 'arg=value'}, dummy_start_response)
        ['value']

        ``response`` should be set as well::

        >>> response
        ('200 OK', [('Content-type', 'text/html')])

        __ https://www.python.org/dev/peps/pep-0333/#the-application-framework\
-side
        """
        env = Environment(env_dict)

        try:
            request = self.request_parser.parse_request(env)
            page = request.page

            if hasattr(page, 'set_request'):
                page.set_request(request)

            if hasattr(page, 'set_cookies'):
                page.set_cookies(env.http_cookie)

            if hasattr(page, 'set_session'):
                session_id = get_or_add_session_id(env.http_cookie)
                page.set_session(self.session_storage[session_id])

            if request.method == 'GET':
                content = page.index(*request.args, **request.kwargs)
                headers = [('Content-type', 'text/html')]
                raise confeitaria.responses.OK(
                    message=content, headers=headers)
            elif request.method == 'POST':
                page.action(*request.args, **request.kwargs)
                raise confeitaria.responses.SeeOther()
        except confeitaria.responses.Response as r:
            status = r.status_code
            headers = r.headers
            content = r.message if r.message is not None else ''

            if status.startswith('30'):
                headers = replace_none_location(headers, request.url)
            headers.extend(get_cookies_tuples(env.http_cookie))

            start_response(status, headers)
            return [content]

    def __enter__(self):
        import multiprocessing
        import inelegant.net

        try:
            self._process = multiprocessing.Process(target=self.run)
            self._process.start()
            inelegant.net.wait_server_up('', self.port, tries=10000)
        except:
            raise

    def __exit__(self, type, value, traceback):
        import inelegant.net

        self._process.terminate()
        inelegant.net.wait_server_down('', self.port, tries=10000)
        self._process = None


def get_cookies_tuples(cookies):
    """
    Returns an iterator. This iterator yields tuples - each tuple defines a
    cookie and is appropriate to be put in the headers list for
    ``wsgiref.start_response()``::

    >>> cookie = Cookie.SimpleCookie()
    >>> cookie['a'] = 'A'
    >>> cookie['b'] = 'B'
    >>> list(get_cookies_tuples(cookie))
    [('Set-Cookie', 'a=A'), ('Set-Cookie', 'b=B')]
    """
    return (
        ('Set-Cookie', cookies[k].OutputString()) for k in cookies
    )


def replace_none_location(headers, location):
    """
    Returns a new list of tuples (with headers values) where any 'Location'
    header with ``None`` as value is replaced by the given location::

    >>> headers = [('Location', None), ('Set-Cookie', 'a=A')]
    >>> replace_none_location(headers, '/b')
    [('Location', '/b'), ('Set-Cookie', 'a=A')]

    Location headers already set are not affected::

    >>> headers = [('Location', '/a'), ('Set-Cookie', 'a=A')]
    >>> replace_none_location(headers, '/b')
    [('Location', '/a'), ('Set-Cookie', 'a=A')]

    """
    return [
        (h[0], location
            if (h[0].lower() == 'location') and (h[1] is None) else h[1])
        for h in headers
    ]


def get_or_add_session_id(cookie):
    """
    Get the session ID from a cookie object::

    >>> import Cookie
    >>> cookie = Cookie.SimpleCookie('Set-Cookie: SESSIONID=123456789ABCDEF')
    >>> get_or_add_session_id(cookie)
    '123456789ABCDEF'

    If the cookie has no session ID...

    ::

    >>> cookie = Cookie.SimpleCookie('')
    >>> 'SESSIONID' in cookie
    False

    ...then one is created...

    ::

    >>> session_id = get_or_add_session_id(cookie)
    >>> session_id  # doctest: +ELLIPSIS
    '...'

    ...and is added to the cookie::

    >>> cookie['SESSIONID'].value == session_id
    True
    """
    if 'SESSIONID' not in cookie:
        session_id = binascii.hexlify(os.urandom(16))
        cookie['SESSIONID'] = session_id
    else:
        session_id = cookie['SESSIONID'].value

    return session_id
