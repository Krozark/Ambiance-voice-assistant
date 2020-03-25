import logging

logger = logging.getLogger(__package__)


class ActionList(list):
    def trigger(self) -> None:
        for i in self:
            i.trigger()

    def set_trigger_kwargs(self, kwargs):
        for i in self:
            i.set_trigger_kwargs(kwargs)

    def __str__(self):
        return "\n".join([i.__str__() for i in self])


class Action(object):
    def __init__(self, *args, name=None, _python=None, **kwargs):
        self._name = name
        self._python = self._get_python(_python)
        self.__trigger_kwargs = dict()

    def _get_python(self, data):
        if not data:
            return None
        if isinstance(data, (tuple, list)):
            data = "\n".join(data)
        return compile(data, "<string>", "exec")

    def _do_trigger(self, **kwargs) -> None:
        raise NotImplemented()

    def set_trigger_kwargs(self, kwargs):
        self.__trigger_kwargs = kwargs

    def trigger(self) -> None:
        if self._python:
            g = {}
            l = self.__trigger_kwargs.copy()
            exec(self._python, g, l)
            self.__trigger_kwargs.update(l)
        logger.debug("Trigger Action '%s' with kwargs=%s", self, self.__trigger_kwargs)
        self._do_trigger(**self.__trigger_kwargs)

    def __str__(self):
        r = self.__class__.__name__
        if self._name:
            r += " ("+ self._name + ")"
        return r