from Ava.core import (
    Action
)


class CallbackAction(Action):
    def __init__(self, callback, *args, **kwargs):
        self._func = callback
        super().__init__(*args, **kwargs)

    def _do_trigger(self, **kwargs) -> None:
        self._func()
