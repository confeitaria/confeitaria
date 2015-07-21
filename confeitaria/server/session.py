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
    def __init__(self):
        self.sessions = {}

    def __getitem__(self, key):
        if key not in self.sessions:
            self.sessions[key] = {}
        return self.sessions[key]

    def __iter__(self):
        return iter(self.sessions)


