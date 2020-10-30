import logging

from Ava.core.utils import (
    WithAva
)

logger = logging.getLogger(__name__)


class TTSFacade(WithAva):
    def say(self, text, sync=True) -> None:
        if self.ava.config.get("audio_as_text"):
            logger.info("TTS '%s'", text)
        else:
            self._say(text, sync=sync)

    def _say(self, text, sync=False) -> None:
        raise NotImplementedError
