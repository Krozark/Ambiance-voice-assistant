from Ava.core import (
    Action
)


class CallbackAction(Action):
    def __init__(self, ava, callback, *args, **kwargs):
        Action.__init__(self, ava, *args, **kwargs)
        self._func = callback

    def _do_trigger(self, **kwargs) -> None:
        self._func()
