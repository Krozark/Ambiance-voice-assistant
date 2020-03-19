import logging

import speech_recognition

from Ava import config
from Ava.audio import RecognizerMixin
from Ava.helpers import IOThread

logger = logging.getLogger(__package__)


class STTWorker(IOThread, RecognizerMixin):
    language = config.LANGUAGE_RECONGITION
    google_key = None

    def __init__(self):
        IOThread.__init__(self)
        RecognizerMixin.__init__(self)

    def _process_input_data(self, audio):
        try:
            value = self._recognizer.recognize_google(audio, language=self.language, key=self.google_key)
            logger.debug(">" + value)
            return value
        except speech_recognition.UnknownValueError:
            logger.debug("Google Speech Recognition could not understand audio")
        except speech_recognition.RequestError as e:
            logger.debug("Could not request results from Google Speech Recognition service; {0}".format(e))
