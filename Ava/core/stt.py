import logging

from Ava.core.facades.stt import STTFacade
from .proxy import ProxyClass

logger = logging.getLogger(__name__)

_STTEngineClass = ProxyClass(STTFacade)


class STTMixin(object):
    _engine_stt = None

    def listen(self, source, phrase_time_limit=5):
        self._ensure_engine(source=source)
        return self._engine_stt.listen(source, phrase_time_limit=phrase_time_limit)

    def _ensure_engine(self, source=None):
        if self._engine_stt is None:
            self._engine_stt = _STTEngineClass()
            if source:
                self._engine_stt.setup(source)
