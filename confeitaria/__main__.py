from . import run

class ExamplePage(object):
     def index(self):
         return """<!doctype html>
         <html>
             <head><title>Confeitaria example page</title></head>
             <body>
                 <h1>Confeitaria example page</h1>
             </body>
         </html>"""

run(ExamplePage())
