import logging

from Ava.settings import settings

logger = logging.getLogger(__name__)


class TTSFacade(object):
    def say(self, text, sync=True) -> None:
        if settings.get("audio_as_text"):
            logger.info("TTS '%s'", text)
        else:
            self._say(text, sync=sync)

    def _say(self, text, sync=False) -> None:
        raise NotImplementedError
