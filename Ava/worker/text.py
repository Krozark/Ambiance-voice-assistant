import logging
import time

import nltk

from Ava import config
from Ava.core import (
    IThread,
    OThread,
    IOThread,
    TTSMixin,
    Worker
)

logger = logging.getLogger(__name__)


# class LoggerWorker(Worker, IThread):
#     def __init__(self, level=logging.DEBUG):
#         Worker.__init__(self)
#         IThread.__init__(self)
#         self._level = level
#
#     def _process_input_data(self, data: str) -> None:
#         logger.log(self._level, data)


class TTSWorker(Worker, IThread, TTSMixin):
    """
    Task that take a text as input and transform it as sound
    """
    def __init__(self, ava, **kwargs):
        Worker.__init__(self, ava, **kwargs)
        IThread.__init__(self)

    def _process_input_data(self, text: str) -> None:
        if text:
            self.say(text)


class FileReaderWorker(Worker, OThread):
    def __init__(self, ava, filename: str, timedelta: int=1, **kwargs):
        Worker.__init__(self, ava, **kwargs)
        OThread.__init__(self)
        self._timedelta = timedelta
        self._sentences = self.get_sentences(filename)

    def get_sentences(self, filename: str) -> list:
        with open(filename, "rt") as f:
            data = f.readlines()
        res = []
        for i in data:
            s = nltk.sent_tokenize(i, self.ava.config.language_data["nltk"])
            res += [x + " . " for x in s if not x.startswith("#")]  # ignore comments + add "." at the end of sentences
        return res

    def run(self) -> None:
        current = 0
        while self._is_running:
            pick = self._sentences[current]
            logger.debug("Next sentence = '%s' ", pick)
            self.output_push(pick)
            time.sleep(self._timedelta)
            current = (current + 1) % len(self._sentences)


class NormalizerWorker(Worker, IOThread):
    def __init__(self, ava, **kwargs):
        Worker.__init__(self, ava, **kwargs)
        IOThread.__init__(self)

    def _process_input_data(self, text: str) -> str:
        logger.debug("Receive data to normalize = '%s'", text)
        normalized = text.strip().lower()
        logger.debug("Normalized as = '%s'", normalized)
        return normalized