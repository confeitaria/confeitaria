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