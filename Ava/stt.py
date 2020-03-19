import logging

import speech_recognition

from Ava import config
from .helpers import (
    IOThread,
    Thread
)

logger = logging.getLogger(__package__)


class RecognizerMixin(object):
    recognizer_class = speech_recognition.Recognizer

    def __init__(self):
        self._recognizer = self.get_recognizer()

    def get_recognizer(self):
        recognizer = self.recognizer_class()
        recognizer.non_speaking_duration = 0.3
        recognizer.pause_threshold = 0.6
        return recognizer

    def adjust_for_ambient_noise(self, source):
        logging.info("A moment of silence, please...")
        self._recognizer.adjust_for_ambient_noise(source, duration=2)
        logger.info("Set minimum energy threshold to {}".format(self.get_energy_threshold()))

    def get_energy_threshold(self):
        return self._recognizer.energy_threshold

    def set_energy_threshold(self, threshold):
        self._recognizer.energy_threshold = threshold

    def listen(self, source):
        return self._recognizer.listen(source, phrase_time_limit=5)


class RecognizerWorker(IOThread, RecognizerMixin):
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


class STTEngine(Thread, RecognizerMixin):
    source_class = speech_recognition.Microphone
    worker_class = RecognizerWorker

    def __init__(self):
        Thread.__init__(self)
        RecognizerMixin.__init__(self)
        self._source = self.get_source()
        self._worker = self.get_worker()

    def get_source(self):
        return self.source_class()

    def get_worker(self):
        return self.worker_class()

    def run(self):
        # start a new thread to recognize audio, while this thread focuses on listening
        self._worker.start()
        with self._source as src:
            self.adjust_for_ambient_noise(src)
            self._worker.set_energy_threshold(self.get_energy_threshold())

            while self._is_running:
                logger.debug("Listen....")
                audio = self.listen(src)
                logger.debug("End Listen....")
                self._worker.input_push(audio)

    def stop(self):
        super().stop()
        self._worker.stop()

    def join(self, timeout=None):
        super().join(timeout=timeout)
        self._worker.join(timeout=timeout)




