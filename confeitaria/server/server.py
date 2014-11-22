import wsgiref.simple_server as simple_server
class Server(object):
    """
    The `Server` objects listen to HTTP requests and serve responses according
    to the page object returned values.
    """
    def __init__(self, page, port=8080):
        self.page = page
        self.port = port
    def run(self):
        """
       This method starts the server up serving the given page.
        A page is an object of a class as the one below:

        >>> class TestPage(object):
        ...     def index(self):
        ...         return "This is a test"

        To run it, just call `confeitaria.run()`, as in:

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
        """
        httpd = simple_server.make_server('', self.port, self._run_app)
        print "Serving on port 8000..."
        httpd.serve_forever()
    def _run_app(self, environ, start_response):
        status = '200 OK'
        headers = [('Content-type', 'text/html')]
        start_response(status, headers)
        return self.page.index()
