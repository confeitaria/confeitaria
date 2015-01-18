"""
A request object should contain the info relevant about the HTTP request.
"""

class Request(object):
    def __init__(self, url_parameters=None):
        self.url_parameters = {} if not url_parameters else url_parameters

