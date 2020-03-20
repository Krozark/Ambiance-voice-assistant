import logging
import time

from Ava import config
from Ava.audio import (
    MicrophoneWorker,
    AudioToFileWorker,
    AudioFilePlayerWorker,
    STTWorker
)

from Ava.text import (
    TTSEngineWorker
)

logger = logging.getLogger(__package__)


class Ava(object):

    def __init__(self):
        """
        Mic --+--> Stt --+--> cache -> Action
              |          |
              |           +-- (if config.DEBUG) --> tss
              |
              +-- (if config.DEBUG_AUDIO) --> save to file --> play



        """
        self._workers = []

        source_worker = MicrophoneWorker()
        stt_worker = STTWorker()
        self._workers += [source_worker, stt_worker]
        source_worker >> stt_worker

        if config.DEBUG_AUDIO:
            save_to_file = AudioToFileWorker("dump")
            play = AudioFilePlayerWorker()
            self._workers += [save_to_file, play]
            source_worker >> (save_to_file >> play)

        if config.DEBUG:
            tss = TTSEngineWorker()
            stt_worker >> tss
            self._workers.append(tss)

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


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    ava = Ava()
    ava.run()
