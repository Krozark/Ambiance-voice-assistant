import logging

from .platform import platform as sys_platform

logger = logging.getLogger(__name__)


class ProxyClass(object):
    def __init__(self, facade, platform=sys_platform):
        object.__init__(self)
        self._object_class = None
        self._platform = platform
        self._facade_class = facade

    def _ensure_object_class(self):
        object_class = self._object_class
        if object_class is None:
            module = "{}.platforms.{}.{}".format(
                self.__module__.rsplit(".", 1)[0],
                self._platform,
                self._facade_class.__module__.split("facades.", 1)[-1]
            )
            try:
                mod = __import__(module, fromlist=['.'])
                object_class = mod.instance_class()
            except ImportError as e:
                logger.warning("impossible to import %s: ", module, e)
                object_class = self._facade_class
            self._object_class = object_class
        return object_class

    def __call__(self, *args, **kwargs):
        klass = self._ensure_object_class()
        return klass(*args, **kwargs)



