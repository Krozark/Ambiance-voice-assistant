import logging

from espeakng import ESpeakNG

from Ava import config
from .base import Action

logger = logging.getLogger(__package__)


class TTSAction(Action):
    language = config.LANGUAGES_INFORMATION_CURRENT["recognition"]

    def __init__(self, sentence, *args, **kwargs):
        self._sentence = sentence
        self._engine = self._get_engine()
        kwargs.setdefault("name", sentence)
        super().__init__(*args, **kwargs)

    def trigger(self) -> None:
        self._engine.say(self._sentence, sync=True)

    def _get_engine(self):
        engine = ESpeakNG()
        engine.voice = config.LANGUAGES_INFORMATION_CURRENT["voice"]
        engine.pitch = 32
        engine.speed = 100
        return engine
