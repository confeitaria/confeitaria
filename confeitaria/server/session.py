import time

class SessionStorage(object):
    """
    ``SessionStorage`` stores and retrieves sessions used by the server. This
    class stores the sessions in memory as actual Python dicts.

    Any session storage should return a new session if a not yet set key is
    requested::

    >>> s = SessionStorage()
    >>> 'key' in s
    False
    >>> s['key']
    {}
    >>> 'key' in s
    True

    Naturally, once a session is created, it should always be retrievable from
    its key::

    >>> session = s['id']
    >>> session['value'] = 'example'
    >>> s['id']['value']
    'example'
    """
    def __init__(self, timeout=30*60):
        self.timeout = timeout
        self.sessions = {}

    def __getitem__(self, key):
        if key in self.sessions:
            session = self.sessions[key]
        else:
            session = Session()

        if time.time() - session.create_time > self.timeout:
            session = Session()

        self.sessions[key] = session

        return session

    def __iter__(self):
        return iter(self.sessions)

class Session(dict):
    """
    ``Session`` objects are dicts used as HTTP sessions::

    >>> s = Session()
    >>> 'key' in s
    False
    >>> s['key'] = 'value'
    >>> 'key' in s
    True
    >>> s['key']
    'value'

    The main difference from dicts is that session objects know the instant they
    were created::

    >>> s.create_time - time.time() < 1
    True
    """
    def __init__(self, create_time=0):
        dict.__init__(self)
        self.create_time = create_time if create_time != 0 else time.time()
