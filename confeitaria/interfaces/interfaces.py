import inspect

class URLedPage(object):
    """
    ``URLedPage`` implements the awareness interface to retrieve the current
    URL - that is, it has a ``set_url()`` method. It also has a ``get_url()``
    method so one can retrieve the set URL.

    To use it you only have to extend it::
    
    >>> class TestPage(URLedPage):
    ...     def index(self):
    ...         return 'url: {0}'.format(self.get_url())
    >>> root = TestPage()
    >>> root.sub = TestPage()
    >>> root.sub.another = TestPage()
    >>> import confeitaria
    >>> import requests
    >>> with confeitaria.Server(root):
    ...     requests.get('http://localhost:8080/').text
    ...     requests.get('http://localhost:8080/sub').text
    ...     requests.get('http://localhost:8080/sub/another').text
    u'url: /'
    u'url: /sub'
    u'url: /sub/another'
    """

    def set_url(self, url):
        self.__url = url

    def get_url(self):
        return self.__url

def has_set_url(page):
    """
    This function returs `True` if the give object has a proper `set_url()`
    method::

    >>> class TestPage(object):
    ...     def set_url(self, url):
    ...         pass
    >>> has_set_url(TestPage())
    True
    """
    result = (
        hasattr(page, 'set_url') and
        inspect.ismethod(page.set_url)
    )

    if not result:
        return False

    args, varargs, keywords, _ = (
        a if a else [] for a in inspect.getargspec(page.set_url)
    )
    args.pop()

    if len(args) - (len(varargs) + len(keywords)) != 1:
        return False

    return True
