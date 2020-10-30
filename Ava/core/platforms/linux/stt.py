import logging

import speech_recognition

from Ava.core.facades.stt import STTFacade

logger = logging.getLogger(__name__)


class LinuxSTT(STTFacade):
    """
    Mixin for class that use recognizer
    @TODO make a android version of this
    """
    __recognizer_class = speech_recognition.Recognizer

    def __init__(self):
        self._recognizer = self.__get_recognizer()

    def _setup(self, source) -> None:
        logger.info("A moment of silence, please...")
        self._recognizer.adjust_for_ambient_noise(source, duration=2)
        logger.info("Set minimum energy threshold = '%s'", self.__get_energy_threshold())

    def _listen(self, source, phrase_time_limit=5):
        return self._recognizer.listen(source, phrase_time_limit=phrase_time_limit)

    def __get_recognizer(self):
        recognizer = self.__recognizer_class()
        recognizer.non_speaking_duration = 0.3
        recognizer.pause_threshold = 0.6
        return recognizer

    def __get_energy_threshold(self) -> int:
        return self._recognizer.energy_threshold


def instance_class():
    return LinuxSTT
