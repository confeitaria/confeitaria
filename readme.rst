=====================================================
Confeitaria, an experimental web framework for Python
=====================================================

Welcome to Confeitaria's documentation! Confeitaria is a Web framework for
Python whose main purpose is to test some hypothesis and possibilities about
Web development. Those hypothesis are the `principles`_ behind Confeitaria.
Let's take a look at them... after some initial tests.

How to use Confeitaria
======================

The very first use to Confeitaria is to see its own documentation. You should
be able to install Confeitaria with ``pip``::

    $ pip install confeitaria

Now, just run

::

    $ python -mconfeitaria

and access http://localhost:8000. Voilà! You will see this same documentation.

Creating and serving pages
--------------------------

You would rather show your own page, for sure. In Confeitaria, a page is an
object with a bounded method named ``index()`` (henceforward named the *index
method*) or a bounded method named ``action()`` (the *action method*). The
*instances* of the class below would be valid pages::

    >>> class TestPage(object):
    ...    def index(self):
    ...        return "This is a test"

The simplest way so far of running a Confeitaria object is to use
``confeitaria.run()``. It starts up a server to serve the return of the
``index()`` method::

    import confeitaria
    page = TestPage()
    confeitaria.run(page)

If you access http://localhost:8000 after this, you will see ``This is a test``
in the browser.

.. One can also create a ``Server`` object, which is more flexible. They are
   created and used as below::
   
       from confeitaria import Server
       page = TestPage()
       server = Server(page)
       server.run()

   A nice ``Server`` trick is to start it up through a ``with`` statement. The
   server will start in a different process, requests would be possible from the
   source code and it would bw shut down after everything is done::
   
       >>> from confeitaria import Server
       >>> import requests
       >>> page = TestPage()
       >>> with Server(page):
       ...     requests.get('http://localhost:8000').text
       u'This is a test'

Subpages
--------

If the page passed to ``confeitaria.run()`` / ``Server`` has an attribute, and
this attribute is also a page, then we only need to add the attribute name as
part of the path in the URL to get its output. The attribute page is a subpage
and can has its own subpages. For example, if we have the classes
below::

    >>> class RootPage(object):
    ...     def index(self):
    ...         return 'root'
    >>> class SubPage(object):
    ...     def index(self):
    ...         return 'a subpage'
    >>> class SubSubPage(object):
    ...     def index(self):
    ...         return 'another subpage'

...and then we build a structure as such::

   >>> root = RootPage()
   >>> root.sub = SubPage()
   >>> root.sub.another = SubSubPage()

... then we should expect the following responses::

    >>> with Server(root):
    ...    requests.get('http://localhost:8000/').text
    ...    requests.get('http://localhost:8000/sub').text
    ...    requests.get('http://localhost:8000/sub/another').text
    u'root'
    u'a subpage'
    u'another subpage'

Index method arguments
----------------------

Naturally, most pages should get information from the browser. This information
can be passed to the index method by arguments. The values for the arguments are
retrieved from the HTTP request parameters. It can be done in two ways:

Query path parameters
    If the index function has mandatory arguments, their values will come
    from the query path, as below::

        >>> class SumPage(object):
        ...    def index(self, p1, p2):
        ...        v1, v2 = int(p1), int(p2)
        ...        return "{0} + {1} = {2}".format(v1, v2, v1 + v2)
        >>> with Server(SumPage()):
        ...     requests.get('http://localhost:8000/3/2').text
        ...     requests.get('http://localhost:8000/-2/3').text
        u'3 + 2 = 5'
        u'-2 + 3 = 1'

    If the URL path does not a value for the given parameter, the index method
    will still be called, having ``None`` as its parameter value::

        >>> class NonePage(object):
        ...    def index(self, arg):
        ...        return "arg: {0}, arg type: {1}".format(arg, type(arg))
        >>> with Server(NonePage()):
        ...     requests.get('http://localhost:8000/').text
        u"arg: None, arg type: <type 'NoneType'>"


    If the URL path has more values than the number of index method's mandatory
    parameters, a 404 Not Found error should be the result::

        >>> class NonePage(object):
        ...    def index(self, arg):
        ...        return "arg: {0} arg type: {1}".format(arg, type(arg))
        >>> with Server(NonePage()):
        ...     requests.get('http://localhost:8000/a/b').status_code
        404

Query string parameters
    If the index function has optional arguments, their values will come
    from the query string parameters, as below::

        >>> class HelloWorldPage(object):
        ...    def index(self, greeting='Hello', greeted='World'):
        ...        return greeting + " " + greeted + "!"
        >>> with Server(HelloWorldPage()):
        ...     requests.get('http://localhost:8000/').text
        ...     requests.get('http://localhost:8000/?greeting=Hi').text
        ...     requests.get(
        ...         'http://localhost:8000/?greeting=Hi&greeted=Earth').text
        u'Hello World!'
        u'Hi World!'
        u'Hi Earth!'

Which one to use is up to the developer. We believe mandatory arguments are
good to pass mandatory identifiers, such as database primary keys and usernames,
as in ``http://example.com/report/1081`` or ``http://example.com/user/juju``.
Optional parameters are nice in most other cases, such as when executing
operations (as in ``http://example.com/user/update?id=324&username=Ju``)
or giving extra options (as in ``http://example.com/report/1081?pages=all``).

    **Advanced warning**: what if one wants to give the values for mandatory
    arguments with query string parameters (e.g. using the URL
    ``http://localhost:8000/?p2=3&p1=2`` to hit ``SumPage``) or optional
    arguments with path components (generating a URL such as
    ``http://localhost:8000/hello/world`` to access ``HelloWorldPage``)? This
    behavior is undefined on purpose. Confeitaria should play well with many
    other frameworks and the best behavior can vary between them. In our
    reference implementation, it fails, and we don't think it is a good practice
    anyway.

Action methods
--------------

Index methods only handle GET requests. If a request uses the POST HTTP method,
it should be handled by an action method.

Action methods are not expected to return HTML documents, they are only called
for their side effects. Any relevant content should be returned by an index
method.

Consider, for example, the following mock of an authetication page::

        >>> class AuthenticationPage(object):
        ...     username = None
        ...     def action(self, username=None):
        ...         AuthenticationPage.username = username

It could be a subpage of a root page as the one below::

        >>> class MainPage(object):
        ...     def index(self):
        ...         if AuthenticationPage.username:
        ...             return 'You are logged in as {0}.'.format(
        ...                 AuthenticationPage.username
        ...             )
        ...         else:
        ...             return 'You are not logged in.'

So we would have this tree::

        >>> page = MainPage()
        >>> page.auth = AuthenticationPage()

By default, nobody would be authenticated::

        >>> with Server(page):
        ...     requests.get('http://localhost:8000/').text
        u'You are not logged in.'

We can, however, send a POST request for log in::

        >>> with Server(page):
        ...     requests.get('http://localhost:8000/').text
        ...     _ = requests.post(
        ...         'http://localhost:8000/auth', data={'username': 'alice'},
        ...         allow_redirects=False # Why to do it? We'll see... soon.
        ...     )
        ...     requests.get('http://localhost:8000/').text
        u'You are not logged in.'
        u'You are logged in as alice.'

Knowing a page URL
------------------

If a page has a bound method named ``set_url()`` which receives one argument,
this method will be called and the parameter value will be the URL of the page.
This means that each page can know what is its own URL on the server::

    >>> class URLAwarePage(object):
    ...     def set_url(self, url):
    ...         self.url = url
    ...     def index(self):
    ...         return 'My URL is ' + self.url
    >>> root = URLAwarePage()
    >>> root.sub = URLAwarePage()
    >>> with Server(root):
    ...     requests.get('http://localhost:8000/').text
    ...     requests.get('http://localhost:8000/sub').text
    u'My URL is /'
    u'My URL is /sub'

This URL is immutable, it is set in the server start up. This means that a page
can even know the URL of its subpages::

    >>> class RootPage(object):
    ...     def __init__(self):
    ...         self.sub = URLAwarePage()
    ...     def index(self):
    ...         return (
    ...             'Subpage is at {0}. '
    ...             '<a href="{0}">Go there!</a>'.format(self.sub.url)
    ...         )
    >>> with Server(RootPage()):
    ...     requests.get('http://localhost:8000/').text
    u'Subpage is at /sub. <a href="/sub">Go there!</a>'

..

    **Note**: one could argue that the "URLs" in these examples are actually
    just paths, not full URLs. We hope, however, to make it possible to a page
    to have a totally different URL, even in another domain. We do not have
    this feature now; yet, assuming that the URLs defined with ``set_url()``
    can be more complex than paths is the way to go - even if the current
    examples are quite simple.

To save you from typing the same method over and over, we also provide the class
``confeitaria.interface.URLedPage``. It implements this protocol and has a
``get_url()`` method::

    >>> import confeitaria.interfaces
    >>> class MyURLedPage(confeitaria.interfaces.URLedPage):
    ...     def index(self):
    ...         return 'My URL is ' + self.get_url()
    >>> root = MyURLedPage()
    >>> root.sub = MyURLedPage()
    >>> with Server(root):
    ...     requests.get('http://localhost:8000/').text
    ...     requests.get('http://localhost:8000/sub').text
    u'My URL is /'
    u'My URL is /sub'

Getting the request
-------------------

If a page has a bound method named ``set_requests()`` with one argument, this
method will be called and the argument value will be an object representing the
HTTP request being processed. This request object can given information, for
example, about query parameters::

    >>> class ActionPage(object):
    ...     def set_request(self, request):
    ...         self.request = request
    ...     def index(self):
    ...         return (
    ...             'The action is ' + self.request.query_parameters['action']
    ...         )
    >>> page = ActionPage()
    >>> with Server(page):
    ...     requests.get('http://localhost:8000/?action=update').text
    u'The action is update'

Getting and sending cookies
---------------------------

Cookies are the most standard way of recalling information between different
requests from the same browser. Once a server sends instructos for setting
cookies to a browser, the browser is expected to send this information back
with each request.

If a page has a bound method named ``set_cookies()`` with one argument, this
method will be called and the argument value will be an object representing a
set of cookies. This cookies object should behave as the
`Cookie.SimpleCookie
<https://docs.python.org/2/library/cookie.html#Cookie.SimpleCookie>`_::

    >>> class AuthenticationPage(object):
    ...     def set_cookies(self, cookies):
    ...         self.cookies = cookies
    ...     def action(self, username=None):
    ...         self.cookies['username'] = username
    ...     def index(self):
    ...         if 'username' in self.cookies:
    ...             return 'Hello {0}'.format(self.cookies['username'].value)
    ...         else:
    ...             return 'Please log in'
    >>> page = AuthenticationPage()
    >>> with Server(page):
    ...     requests.get('http://localhost:8000/').text
    ...     r = requests.post(
    ...         'http://localhost:8000/', data={'username': 'juju'},
    ...         allow_redirects=False
    ...     )
    ...     r.cookies['username']
    ...     requests.get('http://localhost:8000/', cookies=r.cookies).text
    u'Please log in'
    'juju'
    u'Hello juju'

If you extend ``confeitaria.interfaces.CookiedPage`` you will have a pair of
methods to set a retrieve the cookies:

    >>> class AnotherAuthenticationPage(confeitaria.interfaces.CookiedPage):
    ...     def action(self, username=None):
    ...         cookies = self.get_cookies()
    ...         cookies['username'] = username
    ...     def index(self):
    ...         cookies = self.get_cookies()
    ...         if 'username' in cookies:
    ...             return 'Hello {0}'.format(cookies['username'].value)
    ...         else:
    ...             return 'Please log in'
    >>> page = AnotherAuthenticationPage()
    >>> with Server(page):
    ...     requests.get('http://localhost:8000/').text
    ...     r = requests.post(
    ...         'http://localhost:8000/', data={'username': 'juju'},
    ...         allow_redirects=False
    ...     )
    ...     r.cookies['username']
    ...     requests.get('http://localhost:8000/', cookies=r.cookies).text
    u'Please log in'
    'juju'
    u'Hello juju'

Using sessions
--------------

If your page needs to preserve state between requests, you can use sessions. To
get a session, just add a ``set_session()`` method to your page - as usual, it
should receive an argument, which will be a dict-like session object::

    >>> class SessionAuthenticationPage(object):
    ...     def set_session(self, session):
    ...         self.session = session
    ...     def action(self, username=None):
    ...         self.session['username'] = username
    ...     def index(self):
    ...         if 'username' in self.session:
    ...             return 'User: {0}'.format(self.session['username'])
    ...         else:
    ...             return 'Not authenticated'

The received session is preserved between requests. The default implementation
saves the session variables in memory only and preserve the session through
cookies::

    >>> page = SessionAuthenticationPage()
    >>> with Server(page):
    ...     r = requests.get('http://localhost:8000/')
    ...     r.text
    ...     r = requests.post(
    ...         'http://localhost:8000/', data={'username': 'juju'},
    ...         cookies=r.cookies, allow_redirects=False
    ...     )
    ...     requests.get('http://localhost:8000/', cookies=r.cookies).text
    u'Not authenticated'
    u'User: juju'

Note that there is no need to handle the cookies directly: in the server,
Confeitaria takes care of this; in the client, the browser should handle it by
itself.

Redirecting
-----------

HTTP redirect responses are a common need. For example, you may want to redirect
the browser to another URL to where the looked upon content was moved. You just
need to raise the ``confeitaria.responses.MovedPermanently`` exception::

    >>> import confeitaria.responses
    >>> class OldPage(object):
    ...     def index(self):
    ...         raise confeitaria.responses.MovedPermanently('/new')
    >>> class NewPage(object):
    ...     def index(self):
    ...         return 'page: new'
    >>> page = OldPage()
    >>> page.new = NewPage()
    >>> with Server(page):
    ...     r = requests.get('http://localhost:8000/', allow_redirects=False)
    ...     r.status_code
    ...     r.headers['location']
    301
    '/new'
    >>> with Server(page):
    ...     r = requests.get('http://localhost:8000/')
    ...     r.status_code
    ...     r.text
    200
    u'page: new'

If, however, one wants to implement the POST-REDIRECT-GET pattern, it is better
to use the ``SeeOther`` response::

    >>> class LoginPage(object):
    ...     username = None
    ...     def index(self):
    ...         if LoginPage.username is None:
    ...             return 'Nobody is logged in.'
    ...         else:
    ...             return '{0} is logged in.'.format(LoginPage.username)
    ...     def action(self, username=None):
    ...         LoginPage.username = username
    ...         raise confeitaria.responses.SeeOther('/')
    >>> with Server(LoginPage()):
    ...     requests.get('http://localhost:8000/').text
    ...     r = requests.post(
    ...         'http://localhost:8000/', data={'username': 'bob'}
    ...     )
    ...     r.status_code
    ...     r.text
    u'Nobody is logged in.'
    200
    u'bob is logged in.'

If no parameter is given to the ``SeeOther`` or ``MovedPermanently``
constructor, the browser will be redirected to the originally requested URL::

    >>> class RedirectPage(object):
    ...     def action(self, username=None):
    ...         raise confeitaria.responses.SeeOther()
    >>> with Server(RedirectPage()):
    ...     r = requests.post(
    ...         'http://localhost:8000/?a=b', allow_redirects=False
    ...     )
    ...     r.status_code
    ...     r.headers['location']
    303
    '/?a=b'

However, one does not even need to raise the response: if an action method
returns without raising any response, it will redirect to the original URL by
default::

    >>> class MagicRedirectPage(object):
    ...     def action(self, username=None):
    ...         pass
    >>> with Server(MagicRedirectPage()):
    ...     r = requests.post(
    ...         'http://localhost:8000/?magic=true', allow_redirects=False
    ...     )
    ...     r.status_code
    ...     r.headers['location']
    303
    '/?magic=true'

Principles
==========

In Confeitaria, we try to follow some principles as much as possible. We do not
know how much they are feasible or advantageus, they are not necessarily
original and we are not saying you have to follow them. We will try, however.

Principle 1: *The customer should get only the desired piece.*
    Confeitaria should provide many applications, each in its own package. They
    should be as independent as possible so the developer may use only what is
    needed.

Principle 2: *To use a page should be a piece of cake.*
    An application should be pages that can be instatiated many times, maybe
    with some pages. The pages should be as flexible as any simple object, not
    requiring any setup other than being called by ``confeitaria.run()`` (but
    being open to more, optional configuration0.

Principle 3: *A cake should be useful without more cooking.*
    Whenever possible, a Confeitaria package should be usable by only calling
    it with the Python interpreter's ``-m`` flag. For example, the reference
    confeitaria module does provide a feature: it displays this same
    documenation.

Principle 4: *The layered cake should be edible without the frosting.*
    The Confeitaria pages should have tiers, and the lower one cannot depend on
    the higher one. In special, any Confeitaria page should be usable even
    without CSS and JavaScript (the "frosting"). CSS and JavaScript should be
    added to improve the usabiity of a functioning page. A rule of thumb to
    ensure this is that *any task should be executed only using ``curl`` or the
    ``requests`` module*.

Principle 5: *The dough should be tested at each step.*
   We should test as much as possible. Each commit set should contain a new
   test. We should have unit tests, integration tests, functional tests without
   JavaScript and functional tests with JavaScript - probably even JavaScript
   tests.

Principle 6: *The recipes should be written down.*
    We should document how to use Confeitaria. Each public method should have a
    docstring. Each application page should have a separate document explaining
    it. Examples should be doctests.

Principle 7: *Each order should be written down.*
    Each change in the code base should be preceded by a ticket in the issue
    tracker.

Principle 8: *The dough should harmonize with any flavor.*
    It should be possible to run add a Confeitaria page to applications in as
    many frameworks as possible - such as Django, CherryPy, CGI... This WSGI
    implementation is actually a reference implementation - other modules should
    not depend on it!

We may add more principles, or give up some of them - that is acceptable. The
main objective here, after all, is to discover what is possible to do.
