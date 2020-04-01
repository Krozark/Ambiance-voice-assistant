import logging
from typing import List

import spacy
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import word_tokenize

from Ava import config
from Ava.core import (
    IOxThread,
    Worker
)

logger = logging.getLogger(__name__)


class TokenizerSimpleWorker(Worker, IOxThread):
    def __init__(self, ava, **kwargs):
        Worker.__init__(self, ava, **kwargs)
        IOxThread.__init__(self)

    def _process_input_data(self, text: str) -> List[str]:
        for token in word_tokenize(text):
            logger.debug("TokenizerWorker create token %s", token)
            yield token


class TokenizerLemmaWorker(Worker, IOxThread):
    def __init__(self, ava, **kwargs):
        Worker.__init__(self, ava, **kwargs)
        IOxThread.__init__(self)

        logger.info("Loading spacy data. Please wait, this could take a moment...")
        self._nlp = spacy.load(ava.config.language_data["spacy"])
        logger.info("Spacy loaded")

    def _process_input_data(self, data: str) -> List[str]:
        doc = self._nlp(data)
        for token in doc:
            logger.debug("Lemmanize '%s' as '%s'", token, token.lemma_)
            yield token.lemma_


class TokenizerStemWorker(Worker, IOxThread):
    def __init__(self, ava, **kwargs):
        Worker.__init__(self, ava, **kwargs)
        IOxThread.__init__(self)
        self._stemmer = SnowballStemmer(ava.config.language_data["nltk"])

    def _process_input_data(self, data: str) -> str:
        words = word_tokenize(data)
        for w in words:
            token = self._stemmer.stem(w)
            logger.debug("Stemming '%s' as '%s'", w, token)
            yield token

#import spacy
#
#nlp = spacy.load("en_core_web_md")  # make sure to use larger modl!
#tokens = nlp("dog cat banana")
#
#for token1 in tokens:
#    for token2 in tokens:
#        print(token1.text, token2.text, token1.similarity(token2))
