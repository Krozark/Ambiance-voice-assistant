import datetime
import logging
import os

import speech_recognition

from sound_player import Sound

from Ava.core import (
    IOThread,
    OThread,
    IThread,
    STTMixin,
    Worker
)
from Ava.settings import settings

logger = logging.getLogger(__name__)


class MicrophoneWorker(Worker, OThread, STTMixin):
    """
    Class that run a task in background, on put to it's output tha audio listen
    TODO Microphone is platform dependent
    """
    source_class = speech_recognition.Microphone

    def __init__(self, ava, *args, **kwargs):
        Worker.__init__(self, ava, *args, **kwargs)
        OThread.__init__(self)
        STTMixin.__init__(self.ava)
        self._source = self.get_source()

    def get_source(self):
        return self.source_class()

    def run(self):
        with self._source as src:
            while self._is_running:
                logger.debug("Listen....")
                audio = self.listen(src)
                logger.debug("End Listen....")
                self.output_push(audio)
        self.stop()


class AudioToFileWorker(Worker, IOThread):
    """
    Class that take audio as input, and save it to file. The filename is send as output
    TODO Audio to file is platform dependent
    """
    def __init__(self, ava, path=None, **kwargs):
        Worker.__init__(self, ava, **kwargs)
        IOThread.__init__(self)

        self._path = path or ""
        os.makedirs(self._path, exist_ok=True)

    def _process_input_data(self, audio):
        filename = "%s" % datetime.datetime.now()
        p = os.path.join(self._path, filename)
        with open(p, "wb") as f:
            f.write(audio.get_wav_data())
        return p


class AudioFilePlayerWorker(Worker, IThread):
    """
    Task that take a music filename as input and play it
    TODO Audio is platform dependent
    """

    def __init__(self, ava, **kwargs):
        Worker.__init__(self, ava, **kwargs)
        IThread.__init__(self)

    def _process_input_data(self, filename: str) -> None:
        logger.debug("Play file '%s'", filename)
        audio = Sound(filename)
        audio.play()
        audio.wait()


class STTWorker(Worker, IOThread, STTMixin):
    """
    Task that take a audio as input, and output the text of this audio
    TODO STT is platform dependent
    """
    def __init__(self, ava, **kwargs):
        Worker.__init__(self, ava, **kwargs)
        IOThread.__init__(self)
        STTMixin.__init__(self.ava)

    def _process_input_data(self, audio):
        res = None
        try:
            self._ensure_engine()
            res = self._engine_stt._recognizer.recognize_google(  # TODO !!!!!!!!!!!!!!!!
                audio, language=settings.language_data["recognition"],
                key=settings.api_key("GOOGLE_RECOGNITION")
            )
            logger.debug("Recognize: '%s'", res)
        except speech_recognition.UnknownValueError:
            logger.debug("Google Speech Recognition could not understand audio")
            res = "."
        except speech_recognition.RequestError as e:
            logger.debug("Could not request results from Google Speech Recognition service; %s", e)
        return res