import importlib
import logging

logger = logging.getLogger(__package__)


def import_string(dotted_path):
    """
    Import a dotted module path and return the attribute/class designated by the
    last name in the path. Raise ImportError if the import failed.
    """
    try:
        module_path, class_name = dotted_path.rsplit('.', 1)
    except ValueError:
        msg = "%s doesn't look like a module path" % dotted_path
        raise ImportError(msg)

    module = importlib.import_module(module_path)

    try:
        return getattr(module, class_name)
    except AttributeError:
        msg = 'Module "%s" does not define a "%s" attribute/class' % (
            module_path, class_name)
        raise ImportError(msg)


class Factory(object):
    def __init__(self):
        self._mapping = dict()  # [str] : (type, args, kwargs)

    def register(self, key, t, args=None, kwargs=None):
        logger.debug("Register key=%s, type=%s, args=%s, kwargs=%s", key, t, args, kwargs)
        if not t:
            raise ValueError("Registered type cannot be None/null/empty")

        if isinstance(t, str):
            t = import_string(t)
        self._mapping[key] = (
            t,
            args or tuple(),
            kwargs or dict()
        )

    def get(self, key):
        return self._mapping.get(key)

    def construct(self, key, args=None, kwargs=None):
        args = args or tuple()
        kwargs = kwargs or dict()
        try:
            t, a, k = self.get(key)
        except KeyError as e:
            logger.error("Not type registered with key '%s'", key)
            raise
        logger.debug("Construct key=%s, type=%s, defaults args=%s, default kwargs=%s, args=%s, kwargs=%s", key, t, a, k,
                     args, kwargs)
        a = (*a, *args)
        k = {**k, **kwargs}
        obj = t(*a, **k)
        return obj

    def __str__(self):
        r = ""
        for k, v in self._mapping.items():
            r += "[%s]: %s, %s, %s\n" % (k, *v)
        return r


factory = Factory()

#
# class RegisterToFactory(object):
#     def __init__(self, factory_key=None, *args, **kwargs):
#         self._factory_key = factory_key
#         self._args = args
#         self._kwargs = kwargs
#
#     def __call__(self, cls):
#         self._factory_key = self._factory_key or cls.__name__
#         logger.debug("Register '%s' as '%s' to global factory", cls.__name__, self._factory_key)
#         factory.register(
#             self._factory_key,
#             cls,
#             self._args,
#             self._kwargs
#         )
#         return cls
