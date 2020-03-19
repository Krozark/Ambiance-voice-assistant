import logging
import time

from Ava.audio import (
    MicrophoneWorker,
    AudioToFileWorker,
    AudioFilePlayerWorker
)
from Ava.stt import STTWorker

logger = logging.getLogger(__package__)


class Ava(object):

    def __init__(self):
        """
        Mic --+--> save to file --> play
              |
              +--> Stt --+--> tss
                         |
                         + --> cache -> Action
        """
        source_worker = MicrophoneWorker()
        stt_worker = STTWorker()
        save_to_file = AudioToFileWorker("dump")
        play = AudioFilePlayerWorker()
        self._workers = [
            source_worker,
            stt_worker,
            save_to_file,
            play
        ]

        source_worker >> (
            save_to_file >> play,
            stt_worker
        )

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
