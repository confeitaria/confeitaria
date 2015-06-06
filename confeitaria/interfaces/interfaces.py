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
    return has_setter(page, 'url')

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

