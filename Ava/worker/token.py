import logging
from typing import List

import spacy
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import word_tokenize

from Ava.settings import settings
from Ava.core import (
    IOxThread,
    Worker
)

logger = logging.getLogger(__name__)


class Tokenizer(Worker, IOxThread):
    def __init__(self, **kwargs):
        Worker.__init__(self, **kwargs)
        IOxThread.__init__(self)

    def tokenize(self, text: str) -> List[str]:
        raise NotImplementedError()

    def _process_input_data(self, text: str) -> List[str]:
        for token in list(self.tokenize(text)):
            yield token


class TokenizerSimpleWorker(Tokenizer):
    def tokenize(self, text: str) -> List[str]:
        for token in word_tokenize(text):
            logger.debug("TokenizerWorker create token %s", token)
            yield token


class TokenizerLemmaWorker(Tokenizer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        logger.info("Loading spacy data. Please wait, this could take a moment...")
        self._nlp = spacy.load(settings.language_data["spacy"])
        logger.info("Spacy loaded")

    def tokenize(self, text: str) -> List[str]:
        doc = self._nlp(text)
        for token in doc:
            logger.debug("Lemmanize '%s' as '%s'", token, token.lemma_)
            yield token.lemma_


class TokenizerStemWorker(Tokenizer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._stemmer = SnowballStemmer(settings.language_data["nltk"])

    def tokenize(self, text: str) -> List[str]:
        words = word_tokenize(text)
        for w in words:
            token = self._stemmer.stem(w)
            logger.debug("Stemming '%s' as '%s'", w, token)
            yield token
