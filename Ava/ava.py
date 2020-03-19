import logging
import time

from pydub import AudioSegment
from pydub.playback import play

from Ava.stt import STTEngine
from Ava.tts import TTSEngine

logger = logging.getLogger(__package__)


class Base(object):
    stt_engine_class = STTEngine
    tts_engine_class = TTSEngine

    def __init__(self):
        self.tts_engine = self._get_tts_engine()
        self.stt_engine = self._get_stt_engine()

    def get_tts_engine_class(self):
        return self.tts_engine_class

    def _get_tts_engine(self):
        return self.get_tts_engine_class()()

    def get_stt_engine_class(self):
        return self.stt_engine_class

    def _get_stt_engine(self):
        return self.get_stt_engine_class()()


class Ava(Base):
    def run(self):
        self.stt_engine.start()
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass

    def _play(self, filename):
        song = AudioSegment.from_wav(filename)
        play(song)

    def _save(self, audio, filename):
        with open(filename, "wb") as f:
            f.write(audio.get_wav_data())


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    ava = Ava()
    ava.run()
