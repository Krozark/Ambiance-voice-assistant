import datetime
import logging
import os

import speech_recognition
from pydub import AudioSegment
from pydub.playback import play

from Ava import config
from Ava.utils import (
    IOThread,
    OThread,
    IThread,
    RecognizerBase
)

logger = logging.getLogger(__package__)



class MicrophoneWorker(OThread, RecognizerBase):
    """
    Class that run a task in background, on put to it's output tha audio listen
    """
    source_class = speech_recognition.Microphone

    def __init__(self):
        OThread.__init__(self)
        RecognizerBase.__init__(self)
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
        self.stop()


class AudioToFileWorker(IOThread):
    """
    Class that take audio as input, and save it to file. The filename is send as output
    """
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
    """
    Task that take a music filename as input and play it
    """
    def _process_input_data(self, filename: str) -> None:
        logger.debug("Play file '%s'", filename)
        audio = AudioSegment.from_file(filename)
        play(audio)


class STTWorker(IOThread, RecognizerBase):
    """
    Task that take a audio as input, and output the text of this audio
    """
    language = config.LANGUAGES_INFORMATION_CURRENT["recognition"]

    def __init__(self):
        IOThread.__init__(self)
        RecognizerBase.__init__(self)

    def _process_input_data(self, audio):
        try:
            value = self._recognizer.recognize_google(audio, language=self.language, key=config.GOOGLE_RECOGNITION_KEY)
            logger.debug("Recognize: '%s'", value)
            return value
        except speech_recognition.UnknownValueError:
            logger.debug("Google Speech Recognition could not understand audio")
        except speech_recognition.RequestError as e:
            logger.debug("Could not request results from Google Speech Recognition service; %s", e)
        return None
