import unittest

from ..server import Server

class SimplestTestPage(object):

    def index(self):
        return 'simplest test server'

class TestServer(unittest.TestCase):

    def test_serve_page(self):
        import multiprocessing
        import time
        import requests

        page = SimplestTestPage()
        server = Server(page)

        process = multiprocessing.Process(target=server.run)
        process.start()
        time.sleep(1)

        request = requests.get('http://localhost:8080/')
        self.assertEquals(u'simplest test server', request.text)
        self.assertEquals(200, request.status_code)
        self.assertEquals('text/html', request.headers['content-type'])

        process.terminate()

    def test_with(self):
        """
        The Server object should be compatible with the `with` clause.
        """
        import requests

        page = SimplestTestPage()

        with Server(page):
            request = requests.get('http://localhost:8080/')
            self.assertEquals(u'simplest test server', request.text)
            self.assertEquals(200, request.status_code)
            self.assertEquals('text/html', request.headers['content-type'])

if __name__ == "__main__":
    unittest.main()
