"""
A request object should contain the info relevant about the HTTP request.
"""

class Request(object):
    def __init__(self, query_parameters=None):
        self.query_parameters = {} if not query_parameters else query_parameters

