import logging

from espeakng import ESpeakNG

from Ava.core.facades.tts import TTSFacade
from Ava.settings import settings

logger = logging.getLogger(__name__)


class LinuxTTSEngine(TTSFacade):
    def __init__(self):
        super().__init__()
        self._engine = ESpeakNG()
        # engine.pitch = 32
        self._engine.speed = 125
        self._engine.voice = settings.language_data["linux"]["tts"]

    def _say(self, text, sync=False) -> None:
        self._engine.say(text, sync=sync)


def instance_class():
    return LinuxTTSEngine
