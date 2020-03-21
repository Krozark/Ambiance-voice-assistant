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
    FileReaderWorker,
    NormalizerWorker,
    TokenizerWorker,
    LoggerWorker,
    LemmatizerWorker
)

logger = logging.getLogger(__package__)


class Ava(object):

    def __init__(self):
        self._workers = []

        self.create_pipeline(
            audio_input=False,
            debug_audio=False,
            debug_tts=False,
        )

    def add_worker(self, *args):
        for worker in args:
            self._workers.append(worker)

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

    def create_pipeline(self, audio_input=True, debug_audio=False, debug_tts=False):
        """
        (if audio_input)
        MicrophoneWorker --+-- (if debug_audio) --> AudioToFileWorker -> AudioFilePlayerWorker
                           |
                           +--> STTWorker as text_source
        (else)
        FileReaderWorker as text_source
        (end if)


        text_source --+-- (if debug_tts) --> TTSEngineWorker
                      |
                      +--> NormalizerWorker --> LemmatizerWorker --> TokenizerWorker --> cache --> Action
        """
        if audio_input:
            audio_source = MicrophoneWorker()
            self.add_worker(audio_source)
            if debug_audio:
                save_to_file = AudioToFileWorker("debug_audio")
                play = AudioFilePlayerWorker()
                audio_source >> (save_to_file >> play)
                self.add_worker(save_to_file, play)

            text_source = STTWorker()
            self.add_worker(text_source)
            audio_source >> text_source
        else:
            text_source = FileReaderWorker(
                os.path.join(config.LANGUAGES_INFORMATION_CURRENT["dictionary"]),
                timedelta=10
            )
            self._workers.append(text_source)

        if debug_tts:
            tss = TTSEngineWorker()
            text_source >> tss
            self.add_worker(tss)

        normalizer = NormalizerWorker()
        self.add_worker(normalizer)
        text_source >> normalizer

        lemma = LemmatizerWorker()
        self.add_worker(lemma)
        normalizer >> lemma

        # p = LoggerWorker(level=logging.INFO)
        # self.add_worker(p)
        # lemma >> p


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    ava = Ava()
    ava.run()
