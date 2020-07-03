import logging

from Ava.core import (
    Action,
    TTSMixin
)

logger = logging.getLogger(__name__)


class TTSAction(Action, TTSMixin):
    def __init__(self, ava, sentence, *args, **kwargs):
        self._sentence = sentence
        kwargs.setdefault("name", sentence)
        Action.__init__(self, ava, *args, **kwargs)

    def _do_trigger(self, sentence=None, **kwargs) -> None:
        sentence = sentence or self._sentence or ""
        if kwargs:
            sentence = sentence.format(**kwargs)
        self.say(sentence)
