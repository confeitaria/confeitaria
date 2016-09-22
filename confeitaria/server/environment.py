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
import Cookie
import urlparse

try:
    import cStringIO as StringIO
except:
    import StringIO


class Environment(object):
    """
    ``Environment`` represents relevant info from the environment dict in a
    more palatable way. Although you can create one without giving any arg...

    ::

    >>> e = Environment()

    ...it may be more useful if called with an environment dict::

    >>> e = Environment({})

    You can get from it the request method...

    ::

    >>> Environment({'REQUEST_METHOD': 'POST'}).request_method
    'POST'

    ...and the path info::

    >>> Environment({'PATH_INFO': '/example/value'}).path_info
    '/example/value'

    While you can also get the query string...

    ::

    >>> e = Environment({'QUERY_STRING': 'value=example'})
    >>> e.query_string
    'value=example'

    ...you may feel relieved to find it already parsed in the ``query_args``
    attribute::

    >>> e.query_args
    {'value': 'example'}


    There is also available a proper concatenation of path info and
    query string::

    >>> e = Environment(
    ...     {'PATH_INFO': '/example/value', 'QUERY_STRING': 'a=b&c=d'}
    ... )
    >>> e.url
    '/example/value?a=b&c=d'

    If there is a proper content length and input buffer, the environment will
    provide the submitted content as a string::

    >>> e = Environment(
    ...     {
    ...         'CONTENT_LENGTH': len('value=example'),
    ...         'wsgi.input': StringIO.StringIO('value=example')
    ...     }
    ... )
    >>> e.request_body
    'value=example'

    Also, as a parsed dict::

    >>> e.form_args
    {'value': 'example'}

    If cookies are available in the header, you will find them in a
    ``Cookie.SimpleCookie`` object::

    >>> e = Environment({'HTTP_COOKIE': 'a=b'})
    >>> e.http_cookie.output()
    'Set-Cookie: a=b'
    """
    def __init__(
            self, env_dict=None, request_method='GET', path_info='',
            query_string='', content_length=0, content_buffer=None,
            http_cookie=''):
        if env_dict is None:
            env_dict = {}

        self.request_method = env_dict.get('REQUEST_METHOD', request_method)
        self.path_info = env_dict.get('PATH_INFO', path_info)
        self.query_string = env_dict.get('QUERY_STRING', query_string)
        self.query_args = parse_qs_flat(self.query_string)
        self.url = self.path_info + (
            '?' + self.query_string if self.query_string else '')

        http_cookie_string = env_dict.get('HTTP_COOKIE', http_cookie)
        self.http_cookie = Cookie.SimpleCookie(http_cookie_string)

        try:
            content_length = int(env_dict.get('CONTENT_LENGTH', 0))
        except ValueError:
            content_length = 0

        request_body_buffer = env_dict.get('wsgi.input', StringIO.StringIO())
        self.request_body = request_body_buffer.read(content_length)
        self.form_args = parse_qs_flat(self.request_body)


def parse_qs_flat(query_string):
    """
    ``parse_qs_flat()`` works very much like ``urlparse.parse_qs()`` with a
    difference: while the values of the ``urlparse.parse_qs()`` dict are
    lists, in ``parse_qs_flat()`` they are lists only if more than one is
    given; otherwise, the sole value is the dict value. While
    ``urlparse.parse_qs()`` would behave like this::

    >>> import urlparse
    >>> urlparse.parse_qs('a=1')
    {'a': ['1']}


    ``parse_qs_flat()`` takes the value out of the list::

    >>> parse_qs_flat('a=1')
    {'a': '1'}

    ...but only if it a one-value list::

    >>> parse_qs_flat('a=1&b=2&b=3') == {'a': '1', 'b': ['2', '3']}
    True
    """
    query_parameters = urlparse.parse_qs(query_string)

    return {
        k: v[0] if isinstance(v, list) and len(v) == 1 else v
        for k, v in query_parameters.items()
    }
