import inspect
import urlparse

import confeitaria.interfaces
import confeitaria.responses

class RequestParser(object):
    """
    ``RequestParser`` is an implemetation of the URL parser protocol.

    The request parser protocol
    ---------------------------

    Request parsers are objects with a ``parse_request()`` method. This method
    should receive an URL path as an argument and return a request object. This
    request object should give access to at least five attributes:

    * ``page``: a page object;
    * ``path_args``: a list of strings that are the components from the URL
      path not included in the path to the page object;
    * ``query_args``: a dictionary containing the parsed query paramenters;
    *``form_args``: a dictionary containing the parsed body of a POST
      request;
    * ``args``: a list of strings be used as the argument to the index or action
      method; and
    * ``kwargs``: a dictionary, whose values can be string or ``None``,
      containing optional arguments to the index or action method::

        >>> # RequestParser requires such a page to work
        >>> class TestPage(object):
        ...     def index(self, arg, kwarg=None):
        ...         return ''
        >>> request_parser = RequestParser(TestPage())
        >>> request = request_parser.parse_request('/v')
        >>> hasattr(request.page, "index")
        True
        >>> isinstance(request.path_args, list)
        True
        >>> isinstance(request.query_args, dict)
        True
        >>> isinstance(request.form_args, dict)
        True
        >>> isinstance(request.args, list)
        True
        >>> isinstance(request.kwargs, dict)
        True

    It is mandatory that the page index or action method should be called having
    the args list expanded to fill its mandatory arguments, as well as the
    kwargs dict expanded to fill its optional arguments:

        >>> request.page.index(*request.args, **request.kwargs)
        ''

    The ``parse_request()`` method can eventually also throw exceptions
    representing HTTP status codes.

    Parsing POST requests
    ---------------------

    ``parse_request()`` can also receive a second argument, which should be the
    body of a POST request. It is from this argument that the values at
    ``form_args`` will come from::

        >>> class ActionPage(object):
        ...     def action(self, kwarg=None):
        ...         return 'kwarg is ' + kwarg
        >>> request_parser = RequestParser(ActionPage())
        >>> request = request_parser.parse_request('', 'kwarg=example')
        >>> hasattr(request.page, "action")
        True
        >>> isinstance(request.path_args, list)
        True
        >>> isinstance(request.form_args, dict)
        True

    The ``RequestParser`` implemetation
    -----------------------------------

    ``RequestParser`` implements the request parser protocol mapping URLs to a
    tree of objects, following the so called *object publisher* pattern.

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

    We can build ``RequestParser`` passing it as an argument::

        >>> request_parser = RequestParser(page)

    ...and now URL paths should be mapped to the pages of the object. The root
    path is mapped to the root page::

        >>> request = request_parser.parse_request('/')
        >>> request.page == page
        True

    If the path has one more compoment, ``RequestParser`` tries to get a page
    from the attribute (of the root page) with the same name of the path
    component::

        >>> request = request_parser.parse_request('/sub')
        >>> request.page == page.sub
        True

    If the path has yet another component, then the request parser tries to get
    an attribute from the previous subpage, and so on::

        >>> request = request_parser.parse_request('/sub/another')
        >>> request.page == page.sub.another
        True

    On the other hand, if some of the pages do not have an attribute with the
    same name as the next compoment, then an ``confeitaria.responses.NotFound``
    exception is raised to signalize that the page was not found::

        >>> request_parser.parse_request('/nopage')
        Traceback (most recent call last):
          ...
        NotFound: /nopage not found
        >>> request_parser.parse_request('/sub/nopage')
        Traceback (most recent call last):
          ...
        NotFound: /nopage not found

    The same happens when an attribute is found but it is not a page::

        >>> page.attr = object()
        >>> request_parser.parse_request('/attr')
        Traceback (most recent call last):
          ...
        NotFound: /attr not found

    Positional arguments
    --------------------

    There is, however, a situation where the path has compoments that does not
    map to attributes and yet ``parse_request()`` returns a request. It happens
    when the last found page's ``index()`` or ``action()`` method expects
    arguments, and the path has the same number of compoments remaining as the
    number of arguments of the page method.

    An example can make it clearer. Consider the following page::

        >>> class HelloPage(object):
        ...     def index(self, who):
        ...         return 'Hello {0}'.format(who)
        >>> page = HelloPage()
        >>> request_parser = RequestParser(page)

    Since the ``index()`` method expects parameters, we can pass one more
    component in the path::

        >>> request = request_parser.parse_request('/world')
        >>> request.page == page
        True
        >>> request.path_args
        ['world']
        >>> request.page.index(*request.args)
        'Hello world'

    Yet, we cannot pass more path compoments than the number of arguments in the
    method::

        >>> request_parser.parse_request('/world/again')
        Traceback (most recent call last):
          ...
        NotFound: /world/again not found

    Neither can we pass _less_ arguments - ti will also result in a
    ``confeitaria.responses.NotFound`` exception::

    ::
        >>> request = request_parser.parse_request('/')
        Traceback (most recent call last):
          ...
        NotFound: / not found

    Optional parameters
    -------------------

    Index methods can also have optional arguments. They can come from either
    the query parameters or from the submitted form fields. If the latter is
    given, then

    Given for instance the page below::

        >>> class HelloPage(object):
        ...     def index(self, greeting='Hello', greeted='World'):
        ...         return '{0} {1}'.format(greeting, greeted)
        >>> page = HelloPage()
        >>> request_parser = RequestParser(page)

    ...``RequestParser`` will behave this way::

        >>> request = request_parser.parse_request(
        ...     '/?greeting=Hi&greeted=Earth'
        ... )
        >>> request.page == page
        True
        >>> request.path_args
        []
        >>> request.query_args
        {'greeting': 'Hi', 'greeted': 'Earth'}
        >>> request.page.index(*request.path_args, **request.kwargs)
        'Hi Earth'

    Action methods, on the other hand, are not expected to use the query
    arguments as their optional parameters. Instead, it should use the parsed
    values form a POST request body.

    If ``parse_request()`` received the second argument, it is expected to be
    the body of such a POST request, as a string. The parsed values can be found
    at the ``form_args`` attribute from the request::

        >>> class ActionPage(object):
        ...     def action(self, kwarg=None):
        ...         return ''
        >>> page = ActionPage()
        >>> request_parser = RequestParser(page)
        >>> request = request_parser.parse_request('', 'kwarg=example')
        >>> request.page == page
        True
        >>> request.path_args
        []
        >>> request.query_args
        {}
        >>> request.form_args
        {'kwarg': 'example'}
    """

    def __init__(self, page):
        """
        ``RequestParser`` expects as its constructor argument a page
        (probably with subpages) to which to map URLs.
        """
        self.url_dict = self._get_url_dict(page)
        urls = list(self.url_dict.keys())
        urls.sort()
        urls.reverse()
        self.urls = urls

    def parse_request(self, url, body=None):
        _, _, path, _, query, _ = urlparse.urlparse(url)

        page_path = find_longest_prefix(path, self.urls)
        extra_path = path.replace(page_path, '')

        page = self.url_dict[page_path]

        path_args = [a for a in extra_path.split('/') if a]
        query_args = self._get_query_parameters(query)
        form_args = self._get_query_parameters(body)

        if body is None:
            page_method = page.index
            kw_arguments = query_args
        else:
            page_method = page.action
            kw_arguments = form_args

        args_names, _, _, args_values = inspect.getargspec(page_method)
        args_values = args_values if args_values is not None else []

        args = self._get_args(path_args, args_names, args_values)
        kwargs = self._get_kwargs(kw_arguments, args_names, args_values)

        return confeitaria.request.Request(
            page, path_args, query_args, form_args, args, kwargs
        )

    def _get_args(self, positional_arguments, args_names, args_values):
        args_names.pop(0)
        args = positional_arguments[:]

        args_count = len(args_names) - len(args_values)
        if len(args) != args_count:
            raise confeitaria.responses.NotFound(
                message='{0} not found'.format(
                    '/' + '/'.join(positional_arguments)
                )
            )

        return args

    def _get_kwargs(self, kw_arguments, args_names, args_values):
        kwargs_count = len(args_values)
        names = args_names[-kwargs_count:]

        return {
            name: kw_arguments[name] for name in names if name in kw_arguments
        }

    def _get_url_dict(self, page, path=None, url_dict=None):
        url_dict = {} if url_dict is None else url_dict
        path = '' if path is None else path

        url_dict[path] = page

        for attr_name in dir(page):
            attr = getattr(page, attr_name)
            if confeitaria.interfaces.has_page_method(attr):
                url = '/'.join((path, attr_name))
                self._get_url_dict(attr, url, url_dict)

        if confeitaria.interfaces.has_setter(page, 'url'):
            page_url = path if path != '' else '/'
            page.set_url(page_url)

        return url_dict

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
