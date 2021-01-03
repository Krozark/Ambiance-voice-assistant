import logging

from Ava.core.facades.tts import TTSFacade
from .proxy import ProxyClass
from Ava.settings import settings

logger = logging.getLogger(__name__)

_TTSEngineClass = ProxyClass(TTSFacade)


class TTSMixin(object):
    _engine_tts = None

    def say(self, text, sync=True) -> None:
        if settings.get("audio_as_text"):
            logger.info("TTS '%s'", text)
        else:
            self._ensure_engine()
            self._engine_tts.say(text, sync=sync)

    def _ensure_engine(self):
        if self._engine_tts is None:
            self._engine_tts = _TTSEngineClass()
