import logging

from espeakng import ESpeakNG

from .utils import (
    IThread
)

logger = logging.getLogger(__package__)


class TTSEngine:
    """
    Class that implement mechanism for text to speech
    """
    def __init__(self):
        self._engine = self._get_engine()

    def _get_engine(self):
        engine = ESpeakNG()
        engine.voice = "fr"
        engine.pitch = 32
        engine.speed = 150
        return engine

    def say(self, text):
        self._engine.say(text)


class TTSEngineWorker(TTSEngine, IThread):
    """
    Task that tak a text as input and transform it as sound
    """
    def __init__(self):
        TTSEngine.__init__(self)
        IThread.__init__(self)

    def _process_input_data(self, text):
        if text:
            self.say(text)
