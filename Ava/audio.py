import datetime
import logging

import speech_recognition
from pydub import AudioSegment
from pydub.playback import play

from .helpers import (
    IOThread,
    OThread,
    IThread
)
import os
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


class MicrophoneWorker(OThread, RecognizerMixin):
    source_class = speech_recognition.Microphone

    def __init__(self):
        OThread.__init__(self)
        RecognizerMixin.__init__(self)
        self._source = self.get_source()

    def get_source(self):
        return self.source_class()

    def run(self):
        with self._source as src:
            self.adjust_for_ambient_noise(src)

            while self._is_running:
                logger.debug("Listen....")
                audio = self.listen(src)
                logger.debug("End Listen....")
                self.output_push(audio)


class AudioToFileWorker(IOThread):
    def __init__(self, path=None):
        super().__init__()
        self._path = path or ""
        os.makedirs(self._path, exist_ok=True)

    def _process_input_data(self, audio):
        filename = "%s" % datetime.datetime.now()
        p = os.path.join(self._path, filename)
        with open(p, "wb") as f:
            f.write(audio.get_wav_data())
        return p


class AudioFilePlayerWorker(IThread):
    def _process_input_data(self, filename) -> None:
        logger.debug("start to play file '{}'".format(filename))
        song = AudioSegment.from_wav(filename)
        play(song)
        logger.debug("end to play file '{}'".format(filename))
