import inspect

def is_page(obj):
    """
    This function returns ``True`` if its argument has an index method...

    ::

        >>> class ContentPage(object):
        ...     def index(self):
        ...         return 'example'
        >>> is_page(ContentPage())
        True

    ...or an action method::

        >>> class ActionPage(object):
        ...     def index(self):
        ...         return 'example'
        >>> is_page(ActionPage())
        True
    """
    if not inspect.isclass(obj):
        return (
            hasattr(obj, 'index') and
            inspect.ismethod(obj.index)
        ) or (
            hasattr(obj, 'action') and
            inspect.ismethod(obj.action)
        )
    else:
        return False

class RequestedPage(object):
    """
    ``RequestedPage`` implements the awareness interface to retrieve the current
    parsed request - that is, it has a ``set_request()`` method. It also has a
    ``get_request()`` method so one can retrieve the set URL.

    To use it you only have to extend it::
    
    >>> class TestPage(RequestedPage):
    ...     def index(self):
    ...         request = self.get_request()
    ...         return 'value: {0}'.format(request.kwargs['value'])
    >>> page = TestPage()
    >>> import confeitaria.request
    >>> page.set_request(confeitaria.request.Request(args=['value']))
    >>> page.get_request().args
    ['value']
    """

    def set_request(self, request):
        self.__request = request

    def get_request(self):
        return self.__request

def has_set_request(page):
    return has_setter(page, 'request')

class URLedPage(object):
    """
    ``URLedPage`` implements the awareness interface to retrieve the current
    URL - that is, it has a ``set_url()`` method. It also has a ``get_url()``
    method so one can retrieve the set URL.

    To use it you only have to extend it::
    
    >>> class TestPage(URLedPage):
    ...     def index(self):
    ...         return 'url: {0}'.format(self.get_url())
    >>> page = TestPage()
    >>> page.set_url('/test')
    >>> page.get_url()
    '/test'
    """

    def set_url(self, url):
        self.__url = url

    def get_url(self):
        return self.__url

def has_set_url(page):
    return has_setter(page, 'url')

class CookiedPage(object):
    """
    ``CookiedPage`` implements the awareness interface to retrieve cookies from
    the request - that is, it has a ``set_cookies()`` method. It also has a
    ``get_cookies()`` method so one can retrieve the set cookies.

    To use it you only have to extend it::

    >>> import Cookie
    >>> class TestPage(CookiedPage):
    ...     def index(self):
    ...         return 'url: {0}'.format(self.get_cookies())
    >>> page = TestPage()
    >>> cookies = Cookie.SimpleCookie('example=value')
    >>> page.set_cookies(cookies)
    >>> page.get_cookies().output()
    'Set-Cookie: example=value'
    """

    def set_cookies(self, cookies):
        self.__cookies = cookies

    def get_cookies(self):
        return self.__cookies

def has_set_cookies(page):
    return has_setter(page, 'cookies')

class SessionedPage(object):
    """
    ``SessionedPage`` implements the awareness interface to receive the session
    from the current request. The session itself is a dict-like object.

    To use it you only have to extend it::

    >>> class TestPage(SessionedPage):
    ...     def action(self, value=None):
    ...         session = self.get_session()
    ...         session['value'] = 'example'
    ...     def index(self):
    ...         session = self.get_session()
    ...         return 'session value: {0}'.format(session.get('value', None))
    >>> page = TestPage()
    >>> session = {}
    >>> page.set_session(session)
    >>> page.action(value='example')
    >>> page.get_session()
    {'value': 'example'}
    """

    def set_session(self, session):
        self.__session = session

    def get_session(self):
        return self.__session

def has_set_session(page):
    return has_setter(page, 'session')


class Page(URLedPage, RequestedPage, CookiedPage, SessionedPage):
    """
    The ``Page`` class provides the awareness interfaces to get the URL,
    request object, cookies and sessions from a request::

    >>> import confeitaria.request, Cookie, confeitaria.request as cr
    >>> class TestPage(Page):
    ...     def index(self):
    ...         request = self.get_request()
    ...         return ('URL: {0}\\n'
    ...             'Request value: {1}\\n'
    ...             'Cookies: {2}\\n'
    ...             'Session: {3}'
    ...         ).format(
    ...             self.get_url(),
    ...             self.get_request().kwargs['request_value'],
    ...             self.get_cookies().output(),
    ...             self.get_session()
    ...         )
    >>> page = TestPage()
    >>> page.set_url('/test')
    >>> page.set_request(cr.Request(kwargs={'request_value': 'example'}))
    >>> page.set_cookies(Cookie.SimpleCookie('example=value'))
    >>> page.set_session({'session_value': 'example'})
    >>> print(page.index())
    URL: /test
    Request value: example
    Cookies: Set-Cookie: example=value
    Session: {'session_value': 'example'}
    """
    pass

def has_setter(page, attr):
    """
    This function returs ``True`` if the given object has a proper setter method
    for the given attribute

    >>> class TestPage(object):
    ...     def set_url(self, url):
    ...         pass
    >>> has_setter(TestPage(), 'url')
    True

    Note that the setter should have one and only one mandatory argument...

    >>> class NoArgumentTestPage(object):
    ...     def set_url(self):
    ...         pass
    >>> class TwoArgumentsTestPage(object):
    ...     def set_url(self, url1, url2):
    ...         pass
    >>> has_setter(NoArgumentTestPage(), 'url')
    False
    >>> has_setter(TwoArgumentsTestPage(), 'url')
    False

    Also, the method should be bound::

    >>> has_setter(TestPage, 'url')
    False
    """
    method = getattr(page, 'set_' + attr, None)

    result = (
        method is not None and
        inspect.ismethod(method) and
        method.im_self
    )

    if not result:
        return False

    args, _, _, values = (
        a if a else [] for a in inspect.getargspec(method)
    )
    args.pop()

    if len(args) - len(values) != 1:
        return False

    return True

