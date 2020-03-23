import logging

import speech_recognition

logger = logging.getLogger(__package__)


class RecognizerBase(object):
    """Mixin for class that use recognizer"""
    recognizer_class = speech_recognition.Recognizer

    def __init__(self):
        self._recognizer = self.get_recognizer()

    def get_recognizer(self):
        recognizer = self.recognizer_class()
        recognizer.non_speaking_duration = 0.3
        recognizer.pause_threshold = 0.6
        return recognizer

    def adjust_for_ambient_noise(self, source) -> None:
        logging.info("A moment of silence, please...")
        self._recognizer.adjust_for_ambient_noise(source, duration=2)
        logger.info("Set minimum energy threshold = '%s'", self.get_energy_threshold())

    def get_energy_threshold(self) -> int:
        return self._recognizer.energy_threshold

    def set_energy_threshold(self, threshold: int) -> None:
        self._recognizer.energy_threshold = threshold

    def listen(self, source):
        return self._recognizer.listen(source, phrase_time_limit=5)
