import datetime
import logging
import os

import pyaudio
import wave

from sound_player import Sound

from Ava.core import (
    IOThread,
    OThread,
    IThread,
    STTMixin,
    Worker
)
from Ava.settings import (
    settings,
    AUDIO_CHANNELS,
    AUDIO_CHUNK,
    AUDIO_RATE
)

logger = logging.getLogger(__name__)

AUDIO_FORMAT = pyaudio.paInt16


_pyaudio = pyaudio.PyAudio()


class MicrophoneWorker(Worker, OThread):
    """
    Class that run a task in background, on put to it's output tha audio listen
    TODO Microphone is platform dependent (Not Android)
    """

    def __init__(self, *args, **kwargs):
        Worker.__init__(self, *args, **kwargs)
        OThread.__init__(self)
        self._stream = self.get_stream()

    @staticmethod
    def get_stream():
        stream = _pyaudio.open(
            format=AUDIO_FORMAT,
            channels=AUDIO_CHANNELS,
            rate=AUDIO_RATE,
            input=True,
            frames_per_buffer=AUDIO_CHUNK
        )
        return stream

    def run(self):
        self._stream.start_stream()
        while self._is_running:
            logger.debug("Listen....")
            audio = self._stream.read(AUDIO_CHUNK)
            logger.debug("End Listen....")
            if len(audio):
                self.output_push(audio)
        self.stop()


class AudioToFileWorker(Worker, IOThread):
    """
    Class that take audio as input, and save it to file. The filename is send as output
    TODO Audio to file is platform dependent
    """
    def __init__(self, path=None, **kwargs):
        Worker.__init__(self, **kwargs)
        IOThread.__init__(self)

        self._path = path or ""
        os.makedirs(self._path, exist_ok=True)
        self._last_file = None
        self._last_filename = None

    def _process_input_data(self, audio):
        now = datetime.datetime.now()
        filename = now.strftime("%Y-%m-%d %H:%M:%S")
        p = os.path.join(self._path, filename)

        if p != self._last_filename:
            self._last_filename = p
            if self._last_file is not None:
                self._last_file.close()
            self._last_file = wave.open(p, "wb")
            self._last_file.setnchannels(AUDIO_CHANNELS)
            self._last_file.setsampwidth(_pyaudio.get_sample_size(AUDIO_FORMAT))
            self._last_file.setframerate(AUDIO_RATE)

            self._last_file.writeframes(audio)
            return self._last_filename
        return None


class AudioFilePlayerWorker(Worker, IThread):
    """
    Task that take a music filename as input and play it
    TODO Audio is platform dependent
    """

    def __init__(self, **kwargs):
        Worker.__init__(self, **kwargs)
        IThread.__init__(self)

    def _process_input_data(self, filename: str) -> None:
        logger.debug("Play file '%s'", filename)
        audio = Sound(filename)
        audio.play()
        audio.wait()


class STTWorker(Worker, IOThread, STTMixin):
    """
    Task that take a audio as input, and output the text of this audio
    """
    def __init__(self, **kwargs):
        Worker.__init__(self, **kwargs)
        IOThread.__init__(self)
        STTMixin.__init__(self)

    def _process_input_data(self, audio):
        res = self.listen(audio)
        if res:
            logger.debug("Reconize: %s", res)
            return res
        return None