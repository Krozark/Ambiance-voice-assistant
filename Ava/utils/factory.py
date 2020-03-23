class Factory(object):
    def __init__(self):
        self.types = dict()  # [str] : (type, args, kwargs)

    def register(self, key, type, *args, **kwargs):
        self.types[key] = (type, args, kwargs)

    def get(self, key):
        return self.types.get(key)

    def constuct(self, key, *args, **kwargs):
        t, a, k = self.get(key)
        
