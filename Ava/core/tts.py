import logging

from espeakng import ESpeakNG

from Ava import config

logger = logging.getLogger(__package__)


def _get_engine():
    engine = ESpeakNG()
    engine.voice = config.LANGUAGES_INFORMATION_CURRENT["voice"]
    engine.pitch = 32
    engine.speed = 100
    return engine


class TTSMixin(object):
    _engine = _get_engine()

    def say(self, text, sync=True) -> None:
        if config.DEBUG_AUDIO_AS_TEXT:
            logger.info("TTS '%s'", text)
        else:
            self._engine.say(text, sync=sync)
