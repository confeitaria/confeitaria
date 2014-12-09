import inspect
import multiprocessing
import time

import cgi
import wsgiref.simple_server as simple_server

class Server(object):
    """
    The ``Server`` objects listen to HTTP requests and serve responses according
    to the page object returned values.
    """

    def __init__(self, page, port=8080):
        self.linkmap = self._get_linkmap(page)
        urls = list(self.linkmap.keys())
        urls.sort()
        urls.reverse()
        self.urls = urls
        self.port = port
        self._process = None

    def run(self):
        """
        This method starts the server up serving the given page.
        A page is an object of a class as the one below:

        >>> class TestPage(object):
        ...     def index(self):
        ...         return "This is a test"

        To run it, just call `Server.run()`, as in:

        >>> s = Server(TestPage())

        >>> import multiprocessing, time
        >>> p = multiprocessing.Process(target=s.run)
        >>> p.start()
        >>> time.sleep(1)

        Then the server is supposed to serve the content provided by the page:

        >>> import requests
        >>> r = requests.get('http://localhost:8080/')
        >>> r.text
        u'This is a test'
        >>> r.status_code
        200
        >>> r.headers['content-type']
        'text/html'

        >>> p.terminate()

        You can also, mostly for testing purposes, start up a server through a
        ``with`` statement:

        >>> with Server(TestPage()):
        ...     r = requests.get("http://localhost:8080")
        ...     r.text
        u'This is a test'
        """
        httpd = simple_server.make_server('', self.port, self._run_app)
        print "Serving on port 8000..."
        httpd.serve_forever()

    def _run_app(self, environ, start_response):
        path_info = environ.get('PATH_INFO', '')
        url = find_longest_prefix(path_info, self.urls)
        page = self.linkmap[url]
        args = [a for a in path_info.replace(url, '').split('/') if a]

        status = '200 OK'
        headers = [('Content-type', 'text/html')]
        query_parameters = cgi.parse_qs(environ.get('QUERY_STRING', ''))
        for key, value in query_parameters.items():
            if isinstance(value, list) and len(value) == 1:
                query_parameters[key] = value[0]

        names, _, _, values = inspect.getargspec(page.index)
        values = values if values is not None else []
        args_count = len(names) - len(values) -1

        if len(args) > args_count:
            status = '404 Not found'
            start_response(status, headers)
            return '<html><body><h1>{0} not found</h1></body></html>'.format(
                path_info
            )

        missing_args_count = args_count - len(args)
        args += [None] * missing_args_count

        page_parameters = {
            name: value
            for name, value in zip(reversed(names), reversed(values))
        }
        kwargs = {
            name: query_parameters.get(name, value)
            for name, value in page_parameters.items()
        }

        start_response(status, headers)

        return page.index(*args, **kwargs)

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

    def __enter__(self):
        self._process = multiprocessing.Process(target=self.run)
        self._process.start()
        time.sleep(1)

    def __exit__(self, type, value, traceback):
        self._process.terminate()
        self._process = None

def is_page(obj):
    return (
        not inspect.isclass(obj) and
        hasattr(obj, 'index') and
        inspect.ismethod(obj.index)
    )

def find_longest_prefix(string, prefixes):
    longest = ""

    for prefix in prefixes:
        if string.startswith(prefix):
            longest = prefix
            break

    return longest
