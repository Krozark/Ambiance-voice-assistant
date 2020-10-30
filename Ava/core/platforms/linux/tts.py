import logging

from espeakng import ESpeakNG

from Ava.core.facades.tts import TTSFacade

logger = logging.getLogger(__name__)


class LinuxTTSEngine(TTSFacade):
    def __init__(self, ava):
        super().__init__(ava)
        self._engine = ESpeakNG()
        # engine.pitch = 32
        self._engine.speed = 125
        self._engine.voice = self.ava.config.language_data["linux"]["tts"]

    def _say(self, text, sync=False) -> None:
        self._engine.say(text, sync=sync)


def instance_class():
    return LinuxTTSEngine
