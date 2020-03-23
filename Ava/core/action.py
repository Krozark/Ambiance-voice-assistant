class ActionList(list):
    def trigger(self) -> None:
        for i in self:
            i.trigger()

    def __str__(self):
        return "\n".join([i.__str__() for i in self])


class Action(object):
    def __init__(self, name=None):
        self._name = name

    def trigger(self) -> None:
        raise NotImplemented()

    def __str__(self):
        return "%s" % self._name