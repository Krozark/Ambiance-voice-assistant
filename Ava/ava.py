import logging
import os
import time
import enum

from Ava import config
from Ava.worker import (
    MicrophoneWorker,
    AudioToFileWorker,
    AudioFilePlayerWorker,
    STTWorker,
    TTSWorker,
    FileReaderWorker,
    NormalizerWorker,
    SteammerWorker,
    CacheWorker,
    LemmatizerWorker,
    TokenizerWorker,
    ActionWorker,
)
from Ava.action import (
    AudioFilePlayerAction,
    TTSAction
)
from nltk.tokenize import word_tokenize

logger = logging.getLogger(__package__)


class Ava(object):

    class Strategie(enum.Enum):
        tokenizer = 1
        lemmatizer = 2
        stemmer = 3

    def __init__(self):
        self._workers = []
        self._cache = CacheWorker()
        self.create_pipeline(
            audio_input=False,
            debug_audio=False,
            debug_tts=False,
            token_strategie=Ava.Strategie.tokenizer,
        )

    def register(self, sentence, action) -> None:
        self._cache.register(word_tokenize(sentence.lower()), action)

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

    def create_pipeline(self, audio_input=True, debug_audio=False, debug_tts=False, token_strategie=Strategie.tokenizer):
        """
        (if audio_input)
        MicrophoneWorker --+-- (if debug_audio) --> AudioToFileWorker -> AudioFilePlayerWorker
                           |
                           +--> STTWorker as text_source -->
        (else)
        FileReaderWorker as text_source -->
        (end if)


        text_source --+-- (if debug_tts) --> TTSEngineWorker
                      |
                      +--> NormalizerWorker --+ --> (if token_strategie == Ava.Strategie.lemmatizer) LemmatizerWorker as tokenizer -->
                                              |
                                              + --> (elif token_strategie == Ava.Strategie.stemmer) SteammerWorker as tokenizer -->
                                              |
                                              + -->  (else) TokenizerWorker as tokenizer -->

        tokenizer--> CacheWorker --> ActionWorker
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
                os.path.join(config.LANGUAGES_INFORMATION_CURRENT["data-file"]),
                timedelta=20
            )
            self._workers.append(text_source)

        if debug_tts:
            tss = TTSWorker()
            text_source >> tss
            self.add_worker(tss)

        normalizer = NormalizerWorker()
        self.add_worker(normalizer)
        text_source >> normalizer

        if token_strategie == Ava.Strategie.lemmatizer:
            tokenizer = LemmatizerWorker()
        elif token_strategie == Ava.Strategie.stemmer:
            tokenizer = SteammerWorker()
        else:
            tokenizer = TokenizerWorker()
        self.add_worker(tokenizer)
        normalizer >> tokenizer

        # p = LoggerWorker(level=logging.INFO)
        # self.add_worker(p)
        # tokenizer >> p

        self.add_worker(self._cache)
        tokenizer >> self._cache

        action = ActionWorker()
        self.add_worker(action)
        self._cache >> action




if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    ava = Ava()

    ava.register(
        "Ava",
        TTSAction("Oui?")
    )
    ava.register(
        "coucou",
        TTSAction("Tu veux voir ma bite ?")
    )
    ava.register(
        "Comment tu t'appelles",
        TTSAction("Mon nom est Ava")
    )
    ava.register(
        "Qui t'a créé",
        TTSAction("Maxime Barbier")
    )
    ava.register(
        "Qui est maxime barbier",
        TTSAction("Mon créateur")
    )
    ava.register(
        "camion",
        TTSAction("pwet pwet")
    )
    ava.register(
        "1 2 3",
        TTSAction("Soleil")
    )
    ava.register(
        "Que veux-tu faire",
        TTSAction("Je veux t'aider")
    )

    print(ava._cache)

    ava.run()
