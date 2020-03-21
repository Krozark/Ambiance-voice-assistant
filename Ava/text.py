import logging
import time
import random
from espeakng import ESpeakNG
from Ava import config

from .utils import (
    IThread,
    OThread,
    IOThread,
    IOxThread,
)
import spacy
import nltk

logger = logging.getLogger(__package__)


class LoggerWorker(IThread):
    def __init__(self, level=logging.DEBUG):
        super().__init__()
        self._level = level

    def _process_input_data(self, data) -> None:
        logger.log(self._level, data)


class TTSEngineWorker(IThread):
    """
    Task that take a text as input and transform it as sound
    """
    def __init__(self):
        self._engine = self._get_engine()
        IThread.__init__(self)

    def _get_engine(self):
        engine = ESpeakNG()
        engine.voice = config.LANGUAGES_INFORMATION_CURRENT["voice"]
        engine.pitch = 32
        engine.speed = 150
        return engine

    def say(self, text, sync=True):
        self._engine.say(text, sync=sync)

    def _process_input_data(self, text):
        if text:
            self.say(text)


class FileReaderWorker(OThread):
    def __init__(self, filename, timedelta=1):
        super().__init__()
        self._timedelta = timedelta
        self._sentences = self.get_sentences(filename)

    @staticmethod
    def get_sentences(filename):
        with open(filename, "rt") as f:
            data = f.read()
        return nltk.sent_tokenize(data, config.LANGUAGES_INFORMATION_CURRENT["nltk"])

    def run(self) -> None:
        current = 0
        while self._is_running:
            pick = self._sentences[current]
            logger.debug("Next sentence = '%s' ", pick)
            self.output_push(pick)
            time.sleep(self._timedelta)
            current = (current + 1) % len(self._sentences)


class NormalizerWorker(IOThread):
    def _process_input_data(self, text):
        logger.debug("Receive data to normalize = '%s'", text)
        normalized = text.strip().lower()
        logger.debug("Normalized as = '%s'", normalized)
        return normalized


class TokenizerWorker(IOxThread):
    @classmethod
    def _tokenize(cls, sentence):
        token = sentence.split()
        return token

    def _process_input_data(self, text):
        for token in self._tokenize(text):
            yield token


class LemmatizerWorker(IOxThread):
    def __init__(self):
        super().__init__()
        logger.info("Loading spacy, please wait, this could take a moment...")
        self._nlp = spacy.load(config.LANGUAGES_INFORMATION_CURRENT["spacy"])
        logger.info("Spacy loaded")

    def _process_input_data(self, data):
        doc = self._nlp(data)
        for token in doc:
            logger.debug("Lemmanize '%s' as '%s'", token, token.lemma_)
            yield token.lemma_
