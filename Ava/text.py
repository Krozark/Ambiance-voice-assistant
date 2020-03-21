import logging
import time
import random
from espeakng import ESpeakNG
from Ava import config

from .utils import (
    IThread,
    OThread,
    IOThread,
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
        engine.voice = config.LANGUAGES_INFORMATION_CURRENT["voice"]
        engine.pitch = 32
        engine.speed = 150
        return engine

    def say(self, text, sync=True):
        self._engine.say(text, sync=sync)


class TTSEngineWorker(TTSEngine, IThread):
    """
    Task that take a text as input and transform it as sound
    """
    def __init__(self):
        TTSEngine.__init__(self)
        IThread.__init__(self)

    def _process_input_data(self, text):
        if text:
            self.say(text)


class FileReaderWorker(OThread):
    def __init__(self, filename, word_count=1, timedelta=1):
        super().__init__()
        self._timedelta = timedelta
        self._word_count = word_count
        self._dictionary = self.create_tokens(filename)

    @staticmethod
    def create_tokens(filename):
        with open(filename, "rt") as f:
            data = f.read()
        data = data.replace("\n", " ").split(" ")
        return data

    def run(self) -> None:
        while self._is_running:
            pick = " ".join([random.choice(self._dictionary) for x in range(0, self._word_count)])
            logger.debug("Chose '{}'".format(pick))
            self.output_push(pick)
            time.sleep(self._timedelta)


class TokenizerWorker(IOThread):
    @classmethod
    def _normalize_sentence(cls, sentence):
        normalized = sentence.strip().lower()
        return normalized

    @classmethod
    def _tokenize(cls, sentence):
        token = sentence.split()
        return token

    def _process_input_data(self, text):
        tokens = self._tokenize(self._normalize_sentence(text))
        for token in tokens:
            self.output_push(token)


class LoggerWorker(IThread):
    def __init__(self, level=logging.DEBUG):
        super().__init__()
        self._level = level

    def _process_input_data(self, data) -> None:
        logger.log(self._level, data)

