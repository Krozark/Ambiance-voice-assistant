import logging

from espeakng import ESpeakNG

from Ava import config

logger = logging.getLogger(__name__)


def _get_engine():
    engine = ESpeakNG()
    #engine.pitch = 32
    engine.speed = 135
    return engine


class TTSMixin(object):
    _engine = _get_engine()

    def say(self, text, sync=True) -> None:
        if self.ava.config.get("audio_as_text"):
            logger.info("TTS '%s'", text)
        else:
            self._engine.voice = self.ava.config.language_data["voice"]
            self._engine.say(text, sync=sync)
