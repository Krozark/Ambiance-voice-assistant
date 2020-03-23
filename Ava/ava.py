import enum
import json
import logging
import os
import time

from nltk.tokenize import word_tokenize

from Ava import config
from Ava.core import (
    factory as global_factory,
)
from Ava.worker import (
    MicrophoneWorker,
    AudioToFileWorker,
    AudioFilePlayerWorker,
    STTWorker,
    TTSWorker,
    FileReaderWorker,
    NormalizerWorker,
    StemmerWorker,
    CacheWorker,
    LemmatizerWorker,
    TokenizerWorker,
    ActionWorker,
)

logger = logging.getLogger(__package__)


class Ava(object):
    class Strategie(enum.Enum):
        tokenizer = 1
        lemmatizer = 2
        stemmer = 3

    def __init__(self, factory=global_factory):
        self._workers = []
        self._factory = factory
        self._cache = CacheWorker()
        self._register_defaults()

    def load_from_file(self, filename=None):
        if filename is None:
            filename = config.LANGUAGES_INFORMATION_CURRENT["data-file"]

        with open(filename, "rt") as f:
            data = json.loads(f.read())
            self.load(data)

    def load(self, data):
        self._load_pipeline(data.get("pipeline"))
        self._load_types(data.get("types"))
        self._load_register(data.get("register"))

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
                os.path.join(config.LANGUAGES_INFORMATION_CURRENT["input-file"]),
                timedelta=3
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
            tokenizer = StemmerWorker()
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

    def _register_defaults(self):
        # Actions
        self._factory.register("Action:AudioFIlePlayer", "Ava.action.AudioFilePlayerAction",)
        self._factory.register("Action:TTS", "Ava.action.TTSAction")
        # Workers

    def _load_pipeline(self, data):
        kwargs = dict(
            audio_input=False,
            debug_audio=False,
            debug_tts=False,
            token_strategie=Ava.Strategie.tokenizer,
        )
        kwargs.update(data.get("kwargs", dict()))
        self.create_pipeline(**kwargs)

    def _load_types(self, data):
        for alias, value in data.items():
            args = None
            kwargs = None
            if isinstance(value, str):
                t = value
            else:
                t = value["class"]
                args = value.get("args", args)
                kwargs = value.get("kwargs", kwargs)
            self._factory.register(alias, t, args, kwargs)

    def _load_register(self, data_list):
        for data in data_list:
            logger.debug("register data %s", data)
            key = data["key"]
            args = data.get("args", None)
            kwargs = data.get("kwargs", None)
            type_alias = data["type"]

            if args is not None and not isinstance(args, (list, tuple)):
                args = [args]
            obj = self._factory.construct(type_alias, args=args, kwargs=kwargs)
            self.register(key, obj)

    def __str__(self):
        r = "[Ava]\n"
        r += "[Factory]\n%s\n" % ("\n".join(["  " + x for x in self._factory.__str__().split("\n")]))
        r += self._cache.__str__()
        return r


if __name__ == "__main__":
    logger.setLevel(logging.DEBUG)
    logging.basicConfig(level=logging.DEBUG)

    ava = Ava()
    ava.load_from_file()

    logger.info("%s", ava)
    ava.run()
