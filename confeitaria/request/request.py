"""
A request object should contain the info relevant about the HTTP request.
"""

class Request(object):
    def __init__(
            self, page=None, path_args=[], query_args={},
            form_args={}, args=[], kwargs=[]
        ):
        self.page = page
        self.path_args = path_args
        self.query_args = query_args
        self.form_args = form_args
        self.args = args
        self.kwargs = kwargs
