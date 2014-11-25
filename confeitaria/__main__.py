import confeitaria

class BasicDocumentationPage(object):
    """
    This page reads the HTML file ``index.html`` and returns its content for the
    HTTP response.
    """
    def index(self):
        import pkgutil

        return pkgutil.get_data('confeitaria', 'doc/index.html')

confeitaria.run(BasicDocumentationPage())
