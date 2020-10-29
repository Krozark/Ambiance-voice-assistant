import logging
import os

from .utils import (
    WithAva
)
from .platform import platform

logger = logging.getLogger(__name__)


class TTSEngineBase(WithAva):
    def say(self, text, sync=False):
        raise NotImplementedError


TTSEngine = None

if platform == 'linux':
    from espeakng import ESpeakNG

    class LinuxTTSEngine(TTSEngineBase):
        def __init__(self, ava):
            super().__init__(ava)
            self._engine = ESpeakNG()
            # engine.pitch = 32
            self._engine.speed = 125
            self._engine.voice = self.ava.config.language_data["voice"]

        def say(self, text, sync=False):
            self._engine.say(text, sync=sync)

    TTSEngine = LinuxTTSEngine
elif os.name == 'android':
    pass
# elif os.name == 'win':
#     pass


class TTSMixin(object):
    _engine = None

    def say(self, text, sync=True) -> None:
        if self.ava.config.get("audio_as_text"):
            logger.info("TTS '%s'", text)
        else:
            if self._engine is None:
                self._engine = self._setup_engine()
            self._engine.say(text, sync=sync)

    def _setup_engine(self):
        if TTSEngine is not None:
            return TTSEngine(self.ava)
        raise NotImplementedError()


