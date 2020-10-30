import logging

logger = logging.getLogger(__name__)


class STTFacade(object):
    """
    Mixin for class that use recognizer
    """

    def setup(self, source) -> None:
        return self._setup(source)

    def _setup(self, source) -> None:
        raise NotImplementedError

    def listen(self, source, phrase_time_limit=5):
        return self._listen(source, phrase_time_limit=phrase_time_limit)

    def _listen(self, source, phrase_time_limit=5):
        raise NotImplementedError
