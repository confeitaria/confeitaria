"""
A request object should contain the info relevant about the HTTP request.
"""

class Request(object):
    def __init__(
            self, page=None, path_args=None, query_args=None, form_args=None,
            args=None, kwargs=None, url=None, method=None
        ):
        self.page = page
        self.path_args = path_args if path_args is not None else []
        self.query_args = query_args if query_args is not None else {}
        self.form_args = form_args if form_args is not None else {}
        self.args = args if args is not None else []
        self.kwargs = kwargs if kwargs is not None else {}
        self.url = url
        self.method = method
