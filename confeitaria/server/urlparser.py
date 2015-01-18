import inspect
import urlparse

import confeitaria.responses

class ObjectPublisherURLParser(object):
    """
    ``ObjectPublisherURLParser`` is an implemetation of the URL parser protocol.

    The URL parser protocol
    -----------------------

    URL parsers are objects with a ``parse_url()`` method. This method should
    receive a string as an argument and return a tuple with three values. The
    first one is a page object; the second one is a list of strings and the
    third one is a dictionary::

        >>> # ObjectPublisherURLParser requires such a page to work
        >>> class TestPage(object):
        ...     def index(self, arg, kwarg=None):
        ...         return ''
        >>> url_parser = ObjectPublisherURLParser(TestPage())
        >>> page, args, kwargs = url_parser.parse_url('')
        >>> hasattr(page, "index")
        True
        >>> isinstance(args, list)
        True
        >>> isinstance(kwargs, dict)
        True

    It is mandatory that the page index or action method should be called having
    the list expanded to fill its mandatory arguments, as well as the dict
    expanded to fill its optional arguments:

        >>> page.index(*args, **kwargs)
        ''

    The ``parse_url()`` method can eventually also throw exceptions representing
    HTTP status codes.

    Parsing POST requests
    ---------------------

    ``parse_url()`` can also receive a second argument, which should be the body
    of a POST request. In this case, the body will be passed as a string and its
    parameters will be returned in the dict::

        >>> class ActionPage(object):
        ...     def action(self, kwarg=None):
        ...         return ''
        >>> url_parser = ObjectPublisherURLParser(ActionPage())
        >>> action_page, args, kwargs = url_parser.parse_url('', 'kwarg=example')
        >>> hasattr(action_page, "action")
        True
        >>> isinstance(args, list)
        True
        >>> isinstance(kwargs, dict)
        True


    The ``ObjectPublisherURLParser`` implemetation
    ----------------------------------------------

    ``ObjectPublisherURLParser`` implements the URL parser protocol mapping URLs
    to a tree of objects, following the so called *object publisher* pattern.

    Suppose we have the following page classes::

        >>> class RootPage(object):
        ...     def index(self):
        ...         return 'Welcome to the ROOT PAGE'
        >>> class SubPage(object):
        ...     def index(self):
        ...         return 'Welcome to the SUBPAGE'
        >>> class SubSubPage(object):
        ...     def index(self):
        ...         return 'Welcome to the SUBPAGE of the SUBPAGE'

    Then, we build the following object with them::

        >>> page = RootPage()
        >>> page.sub = SubPage()
        >>> page.sub.another = SubSubPage()

    We can build ``ObjectPublisherURLParser`` passing it as an argument::

        >>> url_parser = ObjectPublisherURLParser(page)

    ...and now URL paths should be mapped to the pages of the object. The root
    path is mapped to the root page::

        >>> p, _, _ = url_parser.parse_url('/')
        >>> p == page
        True

    If the path has one more compoment, ``ObjectPublisherURLParser`` tries to
    get a page from the attribute (of the root page) with the same name of the
    path component::

        >>> p, _, _ = url_parser.parse_url('/sub')
        >>> p == page.sub
        True

    If the path has yet another component, then the URL parser tries to get an
    attribute from the previous subpage, and so on::

        >>> p, _, _ = url_parser.parse_url('/sub/another')
        >>> p == page.sub.another
        True

    On the other hand, if some of the pages do not have an attribute with the
    same name as the next compoment, then an ``confeitaria.responses.NotFound``
    exception is raised to signalize that the page was not found::

        >>> url_parser.parse_url('/nopage')
        Traceback (most recent call last):
          ...
        NotFound: /nopage not found
        >>> url_parser.parse_url('/sub/nopage')
        Traceback (most recent call last):
          ...
        NotFound: /nopage not found

    The same happens when an attribute is found but it is not a page::

        >>> page.attr = object()
        >>> url_parser.parse_url('/attr')
        Traceback (most recent call last):
          ...
        NotFound: /attr not found

    Positional arguments
    --------------------

    There is, however, a situation where the path has compoments that does not
    map to attributes and yet ``parse_url()`` returns a tuple. It happens when
    the last found page's ``index()`` method expects arguments, and the path
    has at most the same number of compoments remaining as the number of
    arguments of ``index()``.

    An example can make it clearer. Consider the following page::

        >>> class HelloPage(object):
        ...     def index(self, who):
        ...         return 'Hello {0}'.format(who)
        >>> page = HelloPage()
        >>> url_parser = ObjectPublisherURLParser(page)

    Since the ``index()`` method expects parameters, we can pass one more
    component in the path::

        >>> p, args, _ = url_parser.parse_url('/world')
        >>> p == page
        True
        >>> args
        ['world']
        >>> p.index(*args)
        'Hello world'

    Yet, we cannot pass more path compoment than the number of arguments in the
    method::

        >>> url_parser.parse_url('/world/again')
        Traceback (most recent call last):
          ...
        NotFound: /world/again not found

    (If we pass no parameter, however, the corresponding value in the list of
    arguments will be ``None``.)

    ::
        >>> p, args, _ = url_parser.parse_url('/')
        >>> p == page
        True
        >>> args
        [None]
        >>> p.index(*args)
        'Hello None'

    Optional parameters
    -------------------

    Index methods can also have optional arguments. Those are expected to be
    filled with the dict returned by the URL parser. In the case of the
    ``ObjectPublisherURLParser``, these values comes from the query string.

    Given for instance the page below::

        >>> class HelloPage(object):
        ...     def index(self, greeting='Hello', greeted='World'):
        ...         return '{0} {1}'.format(greeting, greeted)
        >>> page = HelloPage()
        >>> url_parser = ObjectPublisherURLParser(page)

    ...``ObjectPublisherURLParser`` will behave this way::

        >>> p, args, kwargs = url_parser.parse_url(
        ...     '/?greeting=Hi&greeted=Earth'
        ... )
        >>> p == page
        True
        >>> args
        []
        >>> kwargs
        {'greeting': 'Hi', 'greeted': 'Earth'}
        >>> page.index(*args, **kwargs)
        'Hi Earth'

    If ``parse_url()`` received the second argument, then the optional
    parameters should come from this argument, not from the URL query string.
    This second argument is expected to be a body of a POST request as a
    string::

        >>> class ActionPage(object):
        ...     def action(self, kwarg=None):
        ...         return ''
        >>> page = ActionPage()
        >>> url_parser = ObjectPublisherURLParser(page)
        >>> p, args, kwargs = url_parser.parse_url('', 'kwarg=example')
        >>> p == page
        True
        >>> args
        []
        >>> kwargs
        {'kwarg': 'example'}
    """

    def __init__(self, page):
        """
        ``ObjectPublisherURLParser`` expects as its constructor argument a page
        (probably with subpages) to which to map URLs.
        """
        self.linkmap = self._get_linkmap(page)
        urls = list(self.linkmap.keys())
        urls.sort()
        urls.reverse()
        self.urls = urls

    def parse_url(self, url, body=None):
        _, _, path, _, query, _ = urlparse.urlparse(url)

        prefix = find_longest_prefix(path, self.urls)
        page = self.linkmap[prefix]
        query_parameters = self._get_query_parameters(query)

        if body is None:
            page_method = page.index
        else:
            page_method = page.action
            query = body

        args_names, _, _, args_values = inspect.getargspec(page_method)
        args_values = args_values if args_values is not None else []

        args = self._get_args(path.replace(prefix, ''), args_names, args_values)
        kwargs = self._get_kwargs(query, args_names, args_values)

        return confeitaria.request.Request(
            page, args, kwargs, query_parameters=query_parameters
        )

    def _get_args(self, extra_path, args_names, args_values):
        path_args = [a for a in extra_path.split('/') if a]

        args_count = len(args_names) - len(args_values)
        args = path_args

        missing_args_count = len(args_names) - len(path_args) -1
        if missing_args_count > 0:
            args += [None] * missing_args_count
        elif missing_args_count < 0:
            raise confeitaria.responses.NotFound(
                '{0} not found'.format(extra_path)
            )

        return args[:args_count-1]

    def _get_kwargs(self, query, args_names, args_values):
        query_args = urlparse.parse_qs(query)

        for key, value in query_args.items():
            if isinstance(value, list) and len(value) == 1:
                query_args[key] = value[0]

        page_kwargs = {
            name: value
            for name, value in zip(reversed(args_names), reversed(args_values))
        }

        return {
            name: query_args.get(name, value)
            for name, value in page_kwargs.items()
        }

    def _get_linkmap(self, page, path=None, linkmap=None):
        linkmap = {} if linkmap is None else linkmap
        path = '' if path is None else path

        linkmap[path] = page

        for attr_name in dir(page):
            attr = getattr(page, attr_name)
            if is_page(attr):
                self._get_linkmap(attr, '/'.join((path, attr_name)), linkmap)

        try:
            page_url = path if path != '' else '/'
            page.set_url(page_url)
        except:
            pass

        return linkmap

    def _get_query_parameters(self, query):
        query_parameters = urlparse.parse_qs(query)

        for key, value in query_parameters.items():
            if isinstance(value, list) and len(value) == 1:
                query_parameters[key] = value[0]

        return query_parameters

def is_page(obj):
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

def find_longest_prefix(string, prefixes):
    longest = ""

    for prefix in prefixes:
        if string.startswith(prefix):
            longest = prefix
            break

    return longest
