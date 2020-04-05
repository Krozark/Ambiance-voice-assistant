import logging

from .utils import WithAva

logger = logging.getLogger(__name__)


class ActionList(list):
    def trigger(self) -> None:
        for i in self:
            i.trigger()

    def set_trigger_kwargs(self, kwargs):
        for i in self:
            i.set_trigger_kwargs(kwargs)

    def __str__(self):
        return "\n".join([i.__str__() for i in self])


class Action(WithAva):
    def __init__(self, ava, *args, name=None, _python=None, **kwargs):
        WithAva.__init__(self, ava)
        self._name = name
        self._python = self._get_python(_python)
        self._trigger_kwargs = dict()

    def _get_python(self, data):
        if not data:
            return None
        if isinstance(data, (tuple, list)):
            data = "\n".join(data)
        return compile(data, "<string>", "exec")

    def _do_trigger(self, **kwargs) -> None:
        raise NotImplemented()

    def set_trigger_kwargs(self, kwargs) -> None:
        self._trigger_kwargs = kwargs.copy()

    def trigger(self) -> None:
        kwargs = {key.replace("r_", ""): " ".join(value) for key, value in self._trigger_kwargs.items()}
        if self._python:
            glob = {}
            exec(self._python, glob, kwargs)
        logger.debug("Trigger Action '%s' with kwargs=%s", self, kwargs)
        self._do_trigger(**kwargs)

    def __str__(self):
        r = self.__class__.__name__
        if self._name:
            r += " (" + self._name + ")"
        return r


class CallbackAction(Action):
    def __init__(self, ava, callback, *args, **kwargs):
        Action.__init__(self, ava, *args, **kwargs)
        self._func = callback

    def _do_trigger(self, **kwargs) -> None:
        self._func(self)