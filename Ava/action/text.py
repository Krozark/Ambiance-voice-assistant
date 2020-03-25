import logging

from Ava.core import (
    Action,
    TTSMixin
)

logger = logging.getLogger(__package__)


class TTSAction(Action, TTSMixin):
    def __init__(self, sentence, *args, python=None, **kwargs):
        self._sentence = sentence
        kwargs.setdefault("name", sentence)
        super().__init__(*args, **kwargs)



    def _do_trigger(self, **kwargs) -> None:
        if kwargs:
            sentence = self._sentence.format(**kwargs)
        else:
            sentence = self._sentence
        self.say(sentence)