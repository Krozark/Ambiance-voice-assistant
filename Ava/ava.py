import logging
import time
import os

from Ava import config
from Ava.audio import (
    MicrophoneWorker,
    AudioToFileWorker,
    AudioFilePlayerWorker,
    STTWorker
)

from Ava.text import (
    TTSEngineWorker,
    FileTokenizerWorker
)

logger = logging.getLogger(__package__)


class Ava(object):

    def __init__(self):
        self._workers = []

        self.create_pipeline(
            debug_audio=True,#config.DEBUG_AUDIO,
            debug_tts=False# config.DEBUG
        )  # real pipeline with microphone
        # self.create_debug_tss_pipeline()  # pipeline that d'on need microphone

    def run(self):
        for w in self._workers:
            w.start()
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            logger.info("Stopping. Please wait...")

        for w in self._workers:
            w.stop()

        for w in self._workers:
            w.join()

    def create_pipeline(self, debug_audio=False, debug_tts=False):
        """
        Mic --+--> Stt --+--> cache -> Action
              |          |
              |          +-- (if config.DEBUG) --> add_debug_tss_pipeline()
              |
              +-- (if config.DEBUG_AUDIO) --> add_debug_audio_pipeline()
        """

        source_worker = MicrophoneWorker()
        stt_worker = STTWorker()
        self._workers += [source_worker, stt_worker]
        source_worker >> stt_worker

        if debug_audio:
            self.add_debug_audio_pipeline(source_worker)

        if debug_tts:
            self.add_debug_tss_pipeline(stt_worker)

    def add_debug_audio_pipeline(self, audio_source):
        """
        audio_source --> save_to_file --> play
        """
        save_to_file = AudioToFileWorker("dump")
        play = AudioFilePlayerWorker()

        audio_source >> (save_to_file >> play)

        self._workers += [save_to_file, play]

    def add_debug_tss_pipeline(self, text_source):
        """
        text_source --> TTS
        """
        tss = TTSEngineWorker()
        text_source >> tss
        self._workers.append(tss)

    def create_debug_tss_pipeline(self):
        """
        Text --> TTS
        """
        text_source = FileTokenizerWorker(
            os.path.join(config.PROJECT_PATH, "..", "data/liste_francais-utf8.txt"),
            word_count=5,
            timedelta=0.1
        )
        self._workers.append(text_source)
        self.add_debug_tss_pipeline(text_source)
        return text_source


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    ava = Ava()
    ava.run()
