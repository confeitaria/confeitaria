import inspect
import urlparse

import confeitaria.interfaces
import confeitaria.request

from confeitaria.responses import NotFound, MethodNotAllowed

class RequestParser(object):
    """
    ``RequestParser`` is responsible for building a ``Request`` object from a
    URL path and query string and, optionally, the body of a POST request.

    When initialized, the request parser will receive a page - very likely one
    with subpages.

    The magic happens mostly when calling the ``parse_request()`` method. It
    recieves as its argument a dict - more specifically, a WSGI environment.

    As a result, it returns a ``Request`` object, which for its turn has the
    page pointed by the given path - if any - as well as relevant information
    about how to call it. If no page could be found, then a
    ``confeitaria.responses.NotFound`` response is thrown.

    The Object Publisher pattern
    ----------------------------
    ``RequestParser.parse_request()`` returns an stance of
    ``confeitaria.request.Request``. This object has many attributes, and one
    of the most important is ``page``. It is the page object that is pointed by
    the ``PATH_INFO`` value from the environment dict.

    ``RequestParser`` implements the so called *object publisher* pattern, where
    URLs are addresses for real Python objects.

    Suppose we have the following page classes::

    >>> class RootPage(object):
    ...     def index(self):
    ...         return 'root'
    >>> class SubPage(object):
    ...     def index(self):
    ...         return 'sub'
    >>> class AnotherPage(object):
    ...     def index(self):
    ...         return 'another'
    >>> class ArgPage(object):
    ...     def index(self, arg, kwarg='0'):
    ...         return 'arg: {0} kwarg: {1}'.format(arg, kwarg)
    >>> class KwArgPage(object):
    ...     def index(self, kwarg1='1', kwarg2='2'):
    ...         return 'kwarg1: {0} kwarg2: {1}'.format(kwarg1, kwarg2)
    >>> class ActionPage(object):
    ...     def action(self, kwarg1='1', kwarg2='2'):
    ...         pass

    Then, we build the following object with them::

    >>> root = RootPage()
    >>> root.attr = object()
    >>> root.sub = SubPage()
    >>> root.sub.another = AnotherPage()
    >>> root.arg = ArgPage()
    >>> root.kwarg = KwArgPage()
    >>> root.action = ActionPage()

    And then create a request parser as the following::

    >>> parser = RequestParser(root)

    ...and now URL paths should be mapped to the pages of the object. The root
    path is mapped to the root page::

        >>> page = parser.parse_request({'PATH_INFO': '/'}).page
        >>> page.index()
        'root'

    If the path has one more compoment, ``RequestParser`` tries to get a page
    from the attribute (of the root page) with the same name of the path
    component::

        >>> page = parser.parse_request({'PATH_INFO': '/sub'}).page
        >>> page.index()
        'sub'

    If the path has yet another component, then the request parser tries to get
    an attribute from the previous subpage, and so on::

        >>> page = parser.parse_request({'PATH_INFO': '/sub/another'}).page
        >>> page.index()
        'another'

    The ``Request`` object
    ----------------------

    We have seen how the returned object has a ``page`` attribute, but the
    ``confeitaria.request.Request`` object should have at least six
    attributes. They are::

    ``page``
        The page object pointed by the given URL path, if any. It is either the
        page given to the ``RequestParser`` constructor or one of its subpages::

        >>> isinstance(parser.parse_request({'PATH_INFO': '/'}).page, RootPage)
        True
        >>> isinstance(parser.parse_request({'PATH_INFO': '/sub'}).page, SubPage)
        True

    ``path_args``
        The components o the URL path do not necessarily point only to the page.
        If the page method has mandatory arguments, there should be extra
        components in the URL path after a page is found. These extra componets
        will fill the mandatory arguments from the page method from the found
        page. You can find these components are found at the``path_args``
        attribute from the request::

        >>> parser.parse_request({'PATH_INFO': '/arg/value'}).path_args
        ['value']

        If there is no extra compoment, it will be an empty list::

        >>> parser.parse_request({'PATH_INFO': '/sub'}).path_args
        []

    ``query_args``
        A dict containing _all_ values from the query string from the URL.

        >>> parser.parse_request({
        ...     'PATH_INFO': '/', 'QUERY_STRING': 'arg=value'
        ... }).query_args
        {'arg': 'value'}
        >>> parser.parse_request({
        ...     'PATH_INFO': '/sub', 'QUERY_STRING': 'arg=value'
        ... }).query_args
        {'arg': 'value'}
        >>> parser.parse_request({
        ...     'PATH_INFO': '/sub', 'QUERY_STRING': 'arg=value&kwarg1=ok'
        ... }).query_args
        {'kwarg1': 'ok', 'arg': 'value'}

        If the query string is empty, so is the attribute

        >>> parser.parse_request({'PATH_INFO': '/sub'}).query_args
        {}

    ``form_args``
        A dict containing _all_ values from the request body::

        >>> import StringIO
        >>> parser.parse_request({
        ...     'REQUEST_METHOD': 'POST', 'PATH_INFO': '/action',
        ...     'QUERY_STRING': 'arg1=value', 'CONTENT_LENGTH': len('arg2=ok'),
        ...     'wsgi.input': StringIO.StringIO('arg2=ok')
        ... }).form_args
        {'arg2': 'ok'}

        If none is given, it is an empty dict::

        >>> parser.parse_request({
        ...     'PATH_INFO': '/sub', 'QUERY_STRING': 'arg1=value'
        ... }).form_args
        {}

    ``args``
        A sublist of ``path_args`` to be unpacked as the positional arguments of
        the page method from ``page``::

        >>> parser.parse_request({'PATH_INFO': '/arg/value'}).args
        ['value']

        In practice, right now, in this implementation, it will be equal to
        ``path_args`` but some undefined  behaviors can change in the future
        changing this fact.

    ``kwargs``
        A dict to be unpacked as the keyword arguments of ``page`` page method.
        If no request body is given, its values will come from ``query_args``::

        >>> parser.parse_request({
        ...     'PATH_INFO': '/kwarg', 'QUERY_STRING': 'kwarg1=query'   
        ... }).kwargs
        {'kwarg1': 'query'}

        If a request body is available, then its values will come from
        ``form_args``::

        >>> parser.parse_request({
        ...     'REQUEST_METHOD': 'POST', 'PATH_INFO': '/action',
        ...     'QUERY_STRING': 'kwarg1=query',
        ...     'CONTENT_LENGTH': len('kwarg1=form'),
        ...     'wsgi.input': StringIO.StringIO('kwarg1=form')
        ... }).kwargs
        {'kwarg1': 'form'}

        This attribute will only contain values that matches optional arguments
        from the page method to be called - other values from ``form_args`` and
        ``query_args`` are not present::

        >>> parser.parse_request({
        ...     'PATH_INFO': '/kwarg', 'QUERY_STRING': 'kwarg1=query&nothere=true'
        ... }).kwargs
        {'kwarg1': 'query'}
        >>> parser.parse_request({
        ...     'REQUEST_METHOD': 'POST', 'PATH_INFO': '/action',
        ...     'CONTENT_LENGTH': len('kwarg1=form&nothere=true'),
        ...     'wsgi.input': StringIO.StringIO('kwarg1=form&nothere=true')
        ... }).kwargs
        {'kwarg1': 'form'}

        Also, it does not contain values for positional arguments, which always
        should come from the URL path components::

        >>> r = parser.parse_request({
        ...     'PATH_INFO': '/arg/yes', 'QUERY_STRING': 'kwarg=query&arg=no'
        ... })
        >>> r.kwargs
        {'kwarg': 'query'}
        >>> r.args
        ['yes']

    Unpacking ``args`` and ``kwargs`` as the arguments to the page method of the
    provided page should always match::

        >>> r.page.index(*r.args, **r.kwargs)
        'arg: yes kwarg: query'

    Raisig ``NotFound``
    -------------------

    On the other hand, if some of the pages do not have an attribute with the
    same name as the next compoment, then an ``confeitaria.responses.NotFound``
    exception is raised to signalize that the page was not found::

        >>> parser.parse_request({'PATH_INFO': '/nopage'})
        Traceback (most recent call last):
          ...
        NotFound: /nopage not found
        >>> parser.parse_request({'PATH_INFO': '/sub/nopage'})
        Traceback (most recent call last):
          ...
        NotFound: /sub/nopage not found

    The same happens when an attribute is found but it is not a page::

        >>> parser.parse_request({'PATH_INFO': '/attr'})
        Traceback (most recent call last):
          ...
        NotFound: /attr not found

    Positional arguments
    --------------------

    There is, however, a situation where the path has compoments that does not
    map to attributes and yet ``parse_request()`` succeeds. When the last found
    page's ``index()`` or ``action()`` method expects arguments, and the path
    has the same number of compoments remaining as the  number of arguments of
    the page method.

    For example, the index method from ``ArgPage`` expects a positional
    argument. So, any URL hitting the ``ArgPage`` object should have an extra
    component, which will be an argument to the index method::

    Since the ``index()`` method expects parameters, we should pass one more
    component in the path::

        >>> request = parser.parse_request({'PATH_INFO': '/arg/value'})
        >>> request.page.index(*request.args)
        'arg: value kwarg: 0'

    Yet, we cannot pass more path compoments than the number of arguments in the
    method::

        >>> parser.parse_request({'PATH_INFO': '/arg/value/other'})
        Traceback (most recent call last):
          ...
        NotFound: /arg/value/other not found

    Neither can we pass _less_ arguments - it will also result in a
    ``confeitaria.responses.NotFound`` response::

    ::
        >>> parser.parse_request({'PATH_INFO': '/arg'})
        Traceback (most recent call last):
          ...
        NotFound: /arg not found

    Optional parameters
    -------------------

    Index methods can also have optional arguments. They can come from either
    the query string or from the submitted form fields. If the request body is
    not given, then the optional arguments will come from the query string::


    >>> parser.parse_request({
    ...     'PATH_INFO': '/kwarg', 'QUERY_STRING': 'kwarg1=value'
    ... }).kwargs
    {'kwarg1': 'value'}

    Action methods, on the other hand, are not expected to use the query
    arguments as their optional parameters. Instead, it should use the parsed
    values form a POST request body.

    If ``parse_request()`` received the second argument, it is expected to be
    the body of such a POST request, as a string. The parsed values can be found
    at the ``form_args`` attribute from the request::

    >>> parser.parse_request({
    ...     'REQUEST_METHOD': 'POST', 'PATH_INFO': '/action',
    ...     'QUERY_STRING': 'kwarg1=query',
    ...     'CONTENT_LENGTH': len('kwarg1=form'),
    ...     'wsgi.input': StringIO.StringIO('kwarg1=form')
    ... }).kwargs
    {'kwarg1': 'form'}
    """

    def __init__(self, page):
        """
        ``RequestParser`` expects as its constructor argument a page
        (probably with subpages) to which to map URLs.
        """
        self.url_dict = path_dict(
            page, condition=confeitaria.interfaces.has_page_method,
            sep='/', path=''
        )

        for url, page in self.url_dict.items():
            if confeitaria.interfaces.has_setter(page, 'url'):
                page.set_url(url if url != '' else '/')

        urls = list(self.url_dict.keys())
        urls.sort()
        urls.reverse()
        self.urls = urls

    def parse_request(self, environment):
        method = environment.get('REQUEST_METHOD', 'GET')
        path_info = environment.get('PATH_INFO', '')
        query_string = environment.get('QUERY_STRING', '')
        url = path_info + ('?' + query_string if query_string else '')
        try:
            body_size = int(environment.get('CONTENT_LENGTH', 0))
        except (ValueError):
            body_size = 0

        content = environment.get('wsgi.input', None)
        body = content.read(body_size) if content is not None else None

        parsed_url = urlparse.urlparse(url)

        page_path = find_longest_prefix(parsed_url.path, self.urls)
        extra_path = parsed_url.path.replace(page_path, '')

        page = self.url_dict[page_path]

        path_args = [a for a in extra_path.split('/') if a]
        query_args = self._get_query_parameters(parsed_url.query)
        form_args = self._get_query_parameters(body)

        if method == 'POST' and confeitaria.interfaces.has_action_method(page):
            page_method = page.action
            kwargs = form_args
        elif method == 'GET' and confeitaria.interfaces.has_index_method(page):
            page_method = page.index
            kwargs = query_args
        else:
            raise MethodNotAllowed(
                message='{0} does not support {1} requests'.format(url, method)
            )

        argspec = inspect.getargspec(page_method)

        defaults = argspec.defaults if argspec.defaults is not None else []
        args = argspec.args[1:]
        kwargs_count = len(defaults)
        mandatory_args_count = len(args) - kwargs_count

        if len(path_args) != mandatory_args_count:
            raise NotFound(message='{0} not found'.format(url))

        kwargs_names = args[-kwargs_count:]
        kwargs = subdict(kwargs, kwargs_names)

        return confeitaria.request.Request(
            page, path_args, query_args, form_args, path_args, kwargs, url,
            method
        )

    def _get_query_parameters(self, query):
        if query is not None:
            query_parameters = urlparse.parse_qs(query)
        else:
            query_parameters = {}

        for key, value in query_parameters.items():
            if isinstance(value, list) and len(value) == 1:
                query_parameters[key] = value[0]

        return query_parameters

def find_longest_prefix(string, prefixes):
    longest = ""

    for prefix in prefixes:
        if string.startswith(prefix):
            longest = prefix
            break

    return longest

def subdict(d, keys):
    """
    ``subdict()`` receives a dict and a list of strings and return a dict
    containing all values mapped by the list of strings if present in the
    original dict::

    >>> subdict({'a': 1, 'b': 2}, ['a'])
    {'a': 1}

    ``subdict()`  just ignores and key not found in the dict::

    >>> subdict({'a': 1, 'b': 2}, ['a', 'c'])
    {'a': 1}
    """
    return { k: d[k] for k in keys if k in d }

def path_dict(obj, condition, sep='.', path=None):
    """
    ``path_dict()`` receives an object as its argument and returns a dict
    whose keys are the "path" to each attribute of the object (recursively)
    and the values are the attributes. Only objects satisfying a given
    condition will be added to the dict. For the tree below::

    >>> class Obj(object):
    ...     pass
    >>> o = Obj()
    >>> o.sub = Obj()
    >>> o.sub.another = Obj()
    >>> o.sub.another.value = 'a'
    >>> pd = path_dict(o, lambda o: isinstance(o, Obj))

    ...we get this::

    >>> pd[''] == o
    True
    >>> pd['sub'] == o.sub
    True
    >>> pd['sub.another'] == o.sub.another
    True
    >>> 'sub.another.value' in pd
    False

    Or using the example that most interest us - a page tree::

    >>> class TestPage(object):
    ...     def index(self):
    ...         return ''
    >>> page = TestPage()
    >>> page.sub = TestPage()
    >>> page.sub.another = TestPage()
    >>> page.sub.another.value = Obj()

    >>> from confeitaria.interfaces import has_page_method
    >>> pd = path_dict(page, condition=has_page_method, sep='/')
    >>> pd[''] == page
    True
    >>> pd['sub'] == page.sub
    True
    >>> pd['sub/another'] == page.sub.another
    True
    >>> 'sub/another/value' in pd
    False
    """
    result = {}

    if not condition(obj):
        return result
    else:
        result[path if path is not None else ''] = obj

    for an in dir(obj):
        attr = getattr(obj, an)
        if condition(attr):
            attr_path = sep.join((path, an)) if path is not None else an
            attr_dict = path_dict(attr, condition, sep=sep, path=attr_path)
            result.update(attr_dict)

    return result
