"""
A request object should contain the info relevant about the HTTP request.
"""

class Request(object):
    def __init__(self, page=None, args=None, kwargs=None,
            query_parameters=None):
        self.query_parameters = {} if not query_parameters else query_parameters
        self.page = page
        self.args = args
        self.kwargs = kwargs
        self.tuple = (page, args, kwargs)
