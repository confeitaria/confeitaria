import inspect
import urlparse
import collections
try:
    import cStringIO as StringIO
except:
    import StringIO

from  confeitaria.interfaces import \
    has_action_method, has_index_method, has_page_method, has_setter
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
        self.url_dict = path_dict(page, has_page_method, sep='/', path='')

        for url, page in self.url_dict.items():
            if has_setter(page, 'url'):
                page.set_url(url if url != '' else '/')

        self.urls = sorted(self.url_dict.keys(), reverse=True)

    def parse_request(self, environment):
        request_method = environment.get('REQUEST_METHOD', 'GET')
        path_info = environment.get('PATH_INFO', '')
        query_string = environment.get('QUERY_STRING', '')
        url = path_info + ('?' + query_string if query_string else '')
        try:
            body_size = int(environment.get('CONTENT_LENGTH', 0))
        except (ValueError):
            body_size = 0
        content = environment.get('wsgi.input', StringIO.StringIO())
        body = content.read(body_size)

        page_path = first_prefix(path_info, self.urls, default='/')
        extra_path = path_info.replace(page_path, '')
        path_args = [a for a in extra_path.split('/') if a]
        query_args = parse_qs_flat(query_string)
        form_args = parse_qs_flat(body)

        page = self.url_dict[page_path]

        if request_method == 'POST' and has_action_method(page):
            page_method = page.action
            request_kwargs = form_args
        elif request_method == 'GET' and has_index_method(page):
            page_method = page.index
            request_kwargs = query_args
        else:
            raise MethodNotAllowed(
                message='{0} does not support {1} requests'.format(
                    path_info, request_method
                )
            )

        sig = signature(page_method)

        self_count = 1 if page_method.im_self is not None else 0
        if len(path_args) != len(sig.args) - self_count:
            raise NotFound(message='{0} not found'.format(url))

        kwargs = subdict(request_kwargs, sig.kwargs.keys())

        return confeitaria.request.Request(
            page, path_args, query_args, form_args, path_args, kwargs, url,
            request_method
        )

def first_prefix(string, prefixes, default=None):
    """
    Given a list of strings ``l`` and a string ``s``, ``first_prefix()``
    finds the first item from ``l`` that is a prefix for ``s`` (i.e. the
    item ``i`` from ``l`` that satisfies ``s.startswith(i)``::

    >>> first_prefix('abc', ['b', 'a', 'abc'])
    'a'

    By default, if ``first_prefix()`` finds no prefix from the list, it returns
    ``None``::

    >>> first_prefix('jkl', ['b', 'a', 'abc']) is None
    True

    However, if the the ``default`` argument is given, this is the value to be
    returned when o prefix is found::

    >>> first_prefix('jkl', ['b', 'a', 'abc'], default='J')
    'J'
    """
    for p in prefixes:
        if string.startswith(p):
            return p

    return default

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


Signature = collections.namedtuple(
    'Signature', ('args', 'kwargs', 'varargs', 'keywords')
)

def signature(f, exclude_self=False):
    """
    ``signature()`` should return a named tuple representing the argspec of
    the function in a more palatable way. it will have four attributes:

    ``args``
        a list with the name of positional arguments::

            >>> def f(a, b, c=3, d=3.14, e=4, *args, **kwargs): pass
            >>> sig = signature(f)
            >>> sig.args
            ['a', 'b']

        If the function has no arg, ``args`` is an empty list::

            >>> def noarg(): pass
            >>> signature(noarg).args
            []

    ``kwargs``
        a dictionary whose keys are the names of optional arguments mapping
        their default values::

            >>> sig.kwargs == {'c': 3, 'd': 3.14, 'e': 4}
            True

        If there is no optional argument, ``kwargs`` is a empty dict::

            >>> def noopt(): pass
            >>> signature(noopt).kwargs
            {}

    ``varargs``
        the name of the attribute containing the extra positional arguments (the
        "asterisk argument")::

            >>> sig.varargs
            'args'

        It is ``None`` if the function does not expect varargs::

            >>> signature(noarg).varargs is None
            True

    ``keywords``:

        the name of the argument containing the extra keyword values (i.e. the
        "double asterisk arg")::

            >>> sig.keywords
            'kwargs'

        It is ``None`` if the function does not expect extra keyword arguments::

            >>> signature(noarg).keywords is None
            True

    """
    try:
        argspec = inspect.getargspec(f)
    except TypeError:
        if hasattr(f, '__call__'):
            return signature(f.__call__, exclude_self=exclude_self)
        else:
            raise TypeError('{0} is neither a Python function nor callable')

    defaults = argspec.defaults if argspec.defaults is not None else []
    args_count = len(argspec.args) - len(defaults)

    args = argspec.args[:args_count]
    kwargs = dict(zip(argspec.args[args_count:], defaults))

    if exclude_self and getattr(f, 'im_self', False):
        args.pop(0)

    return Signature(args, kwargs, argspec.varargs, argspec.keywords)
