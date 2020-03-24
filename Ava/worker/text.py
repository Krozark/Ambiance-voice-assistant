import logging
import time
from typing import List

import nltk
import spacy
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import word_tokenize

from Ava import config
from Ava.core import (
    IThread,
    OThread,
    IOThread,
    IOxThread,
    TTSMixin
)

logger = logging.getLogger(__package__)


class LoggerWorker(IThread):
    def __init__(self, level=logging.DEBUG):
        super().__init__()
        self._level = level

    def _process_input_data(self, data: str) -> None:
        logger.log(self._level, data)


class TTSWorker(IThread, TTSMixin):
    """
    Task that take a text as input and transform it as sound
    """
    def _process_input_data(self, text: str) -> None:
        if text:
            self.say(text)


class FileReaderWorker(OThread):
    def __init__(self, filename: str, timedelta: int=1):
        super().__init__()
        self._timedelta = timedelta
        self._sentences = self.get_sentences(filename)

    @staticmethod
    def get_sentences(filename: str) -> str:
        with open(filename, "rt") as f:
            data = f.read()
        s = nltk.sent_tokenize(data, config.LANGUAGES_INFORMATION_CURRENT["nltk"])
        return [x for x in s if not x.startswith("#")]

    def run(self) -> None:
        current = 0
        while self._is_running:
            pick = self._sentences[current]
            logger.debug("Next sentence = '%s' ", pick)
            self.output_push(pick)
            time.sleep(self._timedelta)
            current = (current + 1) % len(self._sentences)


class NormalizerWorker(IOThread):
    def _process_input_data(self, text: str) -> str:
        logger.debug("Receive data to normalize = '%s'", text)
        normalized = text.strip().lower()
        logger.debug("Normalized as = '%s'", normalized)
        return normalized


class TokenizerWorker(IOxThread):
    def _process_input_data(self, text: str) -> List[str]:
        for token in word_tokenize(text):
            logger.debug("TokenizerWorker create token %s", token)
            yield token


class LemmatizerWorker(IOxThread):
    def __init__(self):
        super().__init__()
        logger.info("Loading spacy data. Please wait, this could take a moment...")
        self._nlp = spacy.load(config.LANGUAGES_INFORMATION_CURRENT["spacy"])
        logger.info("Spacy loaded")

    def _process_input_data(self, data: str) -> List[str]:
        doc = self._nlp(data)
        for token in doc:
            logger.debug("Lemmanize '%s' as '%s'", token, token.lemma_)
            yield token.lemma_


class StemmerWorker(IOxThread):
    def __init__(self):
        super().__init__()
        self._stemmer = SnowballStemmer(config.LANGUAGES_INFORMATION_CURRENT["nltk"])

    def _process_input_data(self, data: str) -> str:
        words = word_tokenize(data)
        for w in words:
            token = self._stemmer.stem(w)
            logger.debug("Stemming '%s' as '%s'", w, token)
            yield token

#import spacy
#
#nlp = spacy.load("en_core_web_md")  # make sure to use larger model!
#tokens = nlp("dog cat banana")
#
#for token1 in tokens:
#    for token2 in tokens:
#        print(token1.text, token2.text, token1.similarity(token2))
