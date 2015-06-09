"""
A request object should contain the info relevant about the HTTP request.
"""

class Request(object):
    def __init__(
            self, page=None, path_arguments=[], query_arguments={},
            form_arguments={}, args=[], kwargs=[]
        ):
        self.page = page
        self.path_arguments = path_arguments
        self.query_arguments = query_arguments
        self.form_arguments = form_arguments
        self.args = args
        self.kwargs = kwargs
