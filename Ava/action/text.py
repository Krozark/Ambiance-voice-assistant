import logging
import datetime
from Ava.core import (
    Action,
    TTSMixin
)

logger = logging.getLogger(__package__)


class TTSAction(Action, TTSMixin):
    def __init__(self, sentence, *args, python=None, **kwargs):
        self._sentence = sentence
        self._python = self._get_python(python)
        kwargs.setdefault("name", sentence)
        super().__init__(*args, **kwargs)

    def _get_python(self, data):
        if not data:
            return None
        if isinstance(data, (tuple, list)):
            data = "\n".join(data)
        return compile(data, "<string>", "exec")

    def trigger(self) -> None:
        kwargs = {}
        if self._python:
            g = {}
            l = {}
            exec(self._python, g, l)
            kwargs.update(l)
        self.say(
            self._sentence.format(**kwargs)
        )