import logging

from Ava.core import (
    Action,
    TTSMixin
)

logger = logging.getLogger(__name__)


class TTSAction(Action, TTSMixin):
    def __init__(self, sentence, *args, **kwargs):
        self._sentence = sentence
        kwargs.setdefault("name", sentence)
        super().__init__(*args, **kwargs)

    def _do_trigger(self, sentence=None, **kwargs) -> None:
        sentence = sentence or self._sentence or ""
        if kwargs:
            sentence = sentence.format(**kwargs)
        self.say(sentence)