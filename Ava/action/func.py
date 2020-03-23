from Ava.core import (
    Action
)


class CallbackAction(Action):
    def __init__(self, callback, *args, **kwargs):
        self._func = callback
        super().__init__(*args, **kwargs)

    def trigger(self) -> None:
        self._func()
