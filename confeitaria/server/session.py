class SessionStorage(object):
    def __init__(self):
        self.sessions = {}

    def __getitem__(self, key):
        if key not in self.sessions:
            self.sessions[key] = {}
        return self.sessions[key]

    def __iter__(self):
        return iter(self.sessions)


