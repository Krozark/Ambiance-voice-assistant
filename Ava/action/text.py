import logging

from Ava.utils import TTSMixin
from .base import Action

logger = logging.getLogger(__package__)


class TTSAction(Action, TTSMixin):
    def __init__(self, sentence, *args, **kwargs):
        self._sentence = sentence
        kwargs.setdefault("name", sentence)
        super().__init__(*args, **kwargs)

    def trigger(self) -> None:
        self.say(self._sentence)
