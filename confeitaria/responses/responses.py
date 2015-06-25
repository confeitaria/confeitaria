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
    def __init__(self, status_code, headers=None, message=None, *args):
        Exception.__init__(self, message, *args)

        self.status_code = status_code
        try:
            self.headers = headers.items()
        except AttributeError:
            self.headers = [] if headers is None else headers

class MovedPermanently(Response):
    """
    This response redirects the client to a new URL, to which the sought content
    was supposedly moved::

        >>> r = MovedPermanently(location='http://pudim.com.br')
        >>> r.status_code
        '301 Moved Permanently'
        >>> r.headers
        [('Location', 'http://pudim.com.br')]
    """
    status_code = '301 Moved Permanently'
    def __init__(self, location=None, headers=None, message=None, *args):
        headers = [] if not headers else headers
        headers.append(('Location', location))
        Response.__init__(
            self, MovedPermanently.status_code, headers, message, *args
        )
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
    def __init__(self, location=None, headers=None, message=None, *args):
        headers = [] if not headers else headers
        headers.append(('Location', location))
        Response.__init__(self, SeeOther.status_code, headers, message, *args)
        self.location = location

class NotFound(Response):
    """
    This response indicates the requested resource could not be found::

        >>> r = NotFound()
        >>> r.status_code
        '404 Not Found'
    """
    status_code = '404 Not Found'
    def __init__(self, headers=None, message=None, *args):
        Response.__init__(self, NotFound.status_code, headers, message, *args)

class MethodNotAllowed(Response):
    """
    This response indicates the requested resource is available but does not
    handle the requested HTTP method::

        >>> r = MethodNotAllowed()
        >>> r.status_code
        '405 Method Not Allowed'
    """
    status_code = '405 Method Not Allowed'
    def __init__(self, headers=None, message=None, *args):
        Response.__init__(
            self, MethodNotAllowed.status_code, headers, message, *args
        )
