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
    """
    This function returs ``True`` if the give object has a proper ``set_url()``
    method::

    >>> class TestPage(object):
    ...     def set_url(self, url):
    ...         pass
    >>> has_set_url(TestPage())
    True

    Note that the setter should have one and only one mandatory argument...

    >>> class NoArgumentTestPage(object):
    ...     def set_url(self):
    ...         pass
    >>> class TwoArgumentsTestPage(object):
    ...     def set_url(self, url1, url2):
    ...         pass
    >>> has_set_url(NoArgumentTestPage())
    False
    >>> has_set_url(TwoArgumentsTestPage())
    False
    """
    result = (
        hasattr(page, 'set_url') and
        inspect.ismethod(page.set_url) and
        page.set_url.im_self
    )

    if not result:
        return False

    args, varargs, keywords, values = (
        a if a else [] for a in inspect.getargspec(page.set_url)
    )
    args.pop()

    if len(args) - len(values) != 1:
        return False

    return True
