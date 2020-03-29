import enum
import json
import logging
import os
import time

from nltk.tokenize import word_tokenize

from Ava import config
from Ava.core import (
    factory as global_factory,
    Config
)
from Ava.worker import (
    MicrophoneWorker,
    AudioToFileWorker,
    AudioFilePlayerWorker,
    ActionWorker,
    STTWorker,
    TTSWorker,
    FileReaderWorker,
    NormalizerWorker,
    TokenizerSimpleWorker,
    TokenizerStemWorker,
    TokenizerLemmaWorker,
    CacheWorker
)
from json_include import build_json

logger = logging.getLogger(__name__)


class Ava(object):
    class TokenStrategy(enum.Enum):
        simple = 1
        lemma = 2
        stem = 3

    def __init__(self, factory=global_factory):
        super().__init__()
        self.config = Config()
        self._workers = []
        self._factory = factory
        self._cache = CacheWorker(self)
        self._register_defaults()

    def load_from_file(self, filename=None):
        if filename is None:
            filename = os.path.join(config.DATA_PATH, "ava.json")
        data = build_json(filename)
        logger.debug("Load config data: %s", json.dumps(data, indent=2))
        self.load(data)

    def load(self, data):
        config_data = data.get("config", None)
        if config_data:
            self.config.load(config_data)

        self._load_pipeline(data.get("pipeline"))
        self._load_types(data.get("types"))
        self._load_register(data.get("register"))


    def register(self, tokens, action, token_regex=None) -> None:
        self._cache.register(tokens, action, token_regex=token_regex)

    def add_worker(self, worker) -> None:
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

    def create_pipeline(self, audio_input=True, debug_audio=False, debug_tts=False, token_strategy=TokenStrategy.simple):
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
                      +--> NormalizerWorker --+ --> (if token_strategy == Ava.Strategie.lemma) LemmaTokenizerWorker as tokenizer -->
                                              |
                                              + --> (elif token_strategie == Ava.Strategie.stemmer) StemTokenizerWorker as tokenizer -->
                                              |
                                              + -->  (else) TokenizerSimpleWorker as tokenizer -->

        tokenizer--> CacheWorker --> ActionWorker
        """
        if audio_input:
            audio_source = MicrophoneWorker(self)
            if debug_audio:
                save_to_file = AudioToFileWorker("debug_audio")
                play = AudioFilePlayerWorker(self)
                audio_source >> (save_to_file >> play)

            text_source = STTWorker(self)
            audio_source >> text_source
        else:
            text_source = FileReaderWorker(
                self,
                os.path.join(self.config.language_data["input-file"]),
                timedelta=3
            )

        if debug_tts:
            tss = TTSWorker(self)
            text_source >> tss

        normalizer = NormalizerWorker(self)
        text_source >> normalizer

        if token_strategy == Ava.TokenStrategy.lemma:
            tokenizer = TokenizerLemmaWorker(self)
        elif token_strategy == Ava.TokenStrategy.stem:
            tokenizer = TokenizerStemWorker(self)
        else:
            tokenizer = TokenizerSimpleWorker(self)

        normalizer >> tokenizer

        # p = LoggerWorker(level=logging.INFO)
        # self.add_worker(p)
        # tokenizer >> p

        tokenizer >> self._cache

        action = ActionWorker(self)
        self._cache >> action

    def _register_defaults(self):
        # Actions
        #self._factory.register("Action:AudioFIlePlayer", "Ava.action.AudioFilePlayerAction",)
        self._factory.register("Action:TTS", "Ava.action.TTSAction")
        self._factory.register("Action:WebBrowser", "Ava.action.WebBrowserAction")
        self._factory.register("Action:WebBrowserSearch", "Ava.action.WebBrowserSearchAction")
        self._factory.register("Action:WikipediaSearchTTS", "Ava.action.WikipediaSearchTTSAction")
        self._factory.register("Action:WikipediaSearch", "Ava.action.WikipediaSearchAction")
        # Workers

    def _load_pipeline(self, data):
        kwargs = dict(
            audio_input=False,
            debug_audio=False,
            debug_tts=False,
            token_strategy=Ava.TokenStrategy.simple,
        )
        kwargs.update(data.get("kwargs", dict()))
        self.create_pipeline(**kwargs)

    def _load_types(self, data):
        for alias, value in data.items():
            args = []
            kwargs = {}
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
            # get object
            type_type = data["type"]
            type_args = []
            type_kwargs = None
            if isinstance(type_type, dict):
                type_args = type_type.get("args")
                if type_args is not None and not isinstance(type_args, (list, tuple)):
                    type_args = [type_args]
                type_kwargs = type_type.get("kwargs")
                type_type = type_type["type"]
            type_args = [self, *type_args]
            obj = self._factory.construct(type_type, args=type_args, kwargs=type_kwargs)

            # tokens
            tokens_tokens = data["tokens"]
            token_regex = dict()
            if isinstance(tokens_tokens, dict):
                token_regex = tokens_tokens.get("regex")
                tokens_tokens = tokens_tokens.get("tokens", {})

            if isinstance(tokens_tokens, str):
                tokens_tokens = word_tokenize(tokens_tokens)

            if isinstance(tokens_tokens, (tuple, list)):
                tokens_tokens = [x.lower() for x in tokens_tokens]

            self.register(tokens_tokens, obj, token_regex=token_regex)

    def __str__(self):
        r = "[Ava]\n"
        r += "[Factory]\n%s\n" % ("\n".join(["  " + x for x in self._factory.__str__().split("\n")]))
        r += self._cache.__str__()
        return r
