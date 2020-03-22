class ActionList(list):
    def trigger(self, *args, **kwargs) -> None:
        for i in self:
            i.trigger(*args, **kwargs)

    def __str__(self):
        return "\n".join([i.__str__() for i in self])

class Action(object):
    def __init__(self, callback, name=None):
        self._func = callback
        self._name = name or "%s" % callback

    def trigger(self, *args, **kwargs) -> None:
        self._func(*args, **kwargs)

    def __str__(self):
        return "%s" % self._name

