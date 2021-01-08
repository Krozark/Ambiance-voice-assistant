import json
import logging
import os
import time

from json_include import build_json
from sound_player import SoundPlayer

from Ava.core.utils import load_register
from Ava.settings import (
    settings,
    TokenStrategy,
    DATA_PATH,
    AVA_JSON_PATH,
    LANG_PATH,
    REGISTER_FILENAME
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
    ModWorker,
    ConsoleReaderWorker
)

logger = logging.getLogger(__name__)


class Ava(object):
    def __init__(self):
        super().__init__()
        # update settings
        settings.ava = self

        self._running = False

        self._workers = []
        self._tokenizer = None
        self._text_source = None
        self._cache = ModWorker()
        self._player = SoundPlayer()

        self._register_defaults()

    def tokenize(self, text):
        return self._tokenizer.tokenize(text)

    def load_from_file(self, filename=None):
        if filename is None:
            filename = AVA_JSON_PATH
        data = build_json(filename)
        logger.debug("Load config data: %s", json.dumps(data, indent=2))
        self.load(data)

    def load(self, data):
        config_data = data.get("config", None)
        if config_data:
            settings.load(config_data)

        self._load_types(data.get("types"))
        self._load_pipeline(data.get("pipeline"))
        self._load_register()
        self._load_sound_player(data.get("sound-player", {}))

    def register(self, tokens, action, token_regex=None) -> None:
        self._cache.register(tokens, action, token_regex=token_regex)

    def add_worker(self, worker) -> None:
        self._workers.append(worker)

    def stop(self):
        logger.info("Stopping Ava ...")
        self._running = False
        self._player.stop()
        for w in self._workers:
            w.stop()
        logger.info("Stopping Ava done.")

    def run(self, blocking=True):
        logger.info("Starting Ava ...")
        self._running = True
        for w in self._workers:
            w.start()
        self._player.play()

        logger.info("Starting Ava done.")
        if blocking:
            try:
                while self._running :
                    time.sleep(0.1)
            except KeyboardInterrupt:
                logger.info("Stopping. Please wait ...")

            self.stop()
            self.join()

    def join(self):
        logger.info("Joining Ava ...")
        for w in self._workers:
            w.join()
        logger.info("Joining Ava done.")

    def create_pipeline(self, text_input=True, debug_audio=False, debug_tts=False):
        """
        (if text_input == audio)
        MicrophoneWorker --+-- (if debug_audio) --> AudioToFileWorker -> AudioFilePlayerWorker
                           |
                           +--> STTWorker as text_source -->
        (elif text_input == "file")
        FileReaderWorker as text_source -->
        (else)
        ConsoleReaderWorker as text_source -->
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
        if text_input == "audio":
            audio_source = MicrophoneWorker()
            if debug_audio:
                save_to_file = AudioToFileWorker("debug_audio")
                play = AudioFilePlayerWorker()
                audio_source >> (save_to_file >> play)

            self._text_source = STTWorker()
            audio_source >> self._text_source
        elif text_input == "file":
            self._text_source = FileReaderWorker(
                os.path.join(settings.language_data["input-file"]),
                timedelta=3
            )
        else:
            self._text_source = ConsoleReaderWorker()

        if debug_tts:
            tss = TTSWorker()
            self._text_source >> tss

        normalizer = NormalizerWorker()
        self._text_source >> normalizer

        if settings.token_strategy == TokenStrategy.lemma.value:
            self._tokenizer = TokenizerLemmaWorker()
        elif settings.token_strategy == TokenStrategy.stem.value:
            self._tokenizer = TokenizerStemWorker()
        else:
            self._tokenizer = TokenizerSimpleWorker()

        normalizer >> self._tokenizer

        self._tokenizer >> self._cache

        action = ActionWorker()
        self._cache >> action

    def _register_defaults(self):
        # Mod
        settings.factory.register("Ava:Mod", "Ava.core.mod.Mod")
        # Actions
        settings.factory.register("Ava:Action:AudioFilePlayer", "Ava.action.AudioFilePlayerAction",)
        settings.factory.register("Ava:Action:AudioStop", "Ava.action.AudioStopAction",)
        settings.factory.register("Ava:Action:Stop", "Ava.action.AvaStopAction")
        settings.factory.register("Ava:Action:TTS", "Ava.action.TTSAction")
        settings.factory.register("Ava:Action:WebBrowser", "Ava.action.WebBrowserAction")
        settings.factory.register("Ava:Action:WebBrowserSearch", "Ava.action.WebBrowserSearchAction")
        settings.factory.register("Ava:Action:WikipediaSearchTTS", "Ava.action.WikipediaSearchTTSAction")
        settings.factory.register("Ava:Action:WikipediaSearch", "Ava.action.WikipediaSearchAction")
        settings.factory.register("Ava:Action:Weather", "Ava.action.WeatherAction")

        # Workers

    def _load_pipeline(self, data):
        kwargs = dict(
            text_input="console",
            debug_audio=False,
            debug_tts=False
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
            settings.factory.register(alias, t, args, kwargs)

    def _load_register(self):
        filename = os.path.join(LANG_PATH, settings.get_language(), REGISTER_FILENAME)
        data_list = build_json(filename)
        logger.debug("Load registration data: %s", json.dumps(data_list, indent=2))
        load_register(data_list, self)

    def _load_sound_player(self, data):
        for key, value in data.items():
            for key2, value2 in value.items():
                if key2 == "concurency":
                    self._player._playlists[key].set_concurency(int(value2))
                elif key2 == "replace":
                    self._player._playlists[key].set_replace(bool(value2))
                elif key2 == "loop":
                    self._player._playlists[key].set_loop(int(value2))

    def dump(self):
        r = "[Ava]\n"
        r += "[Factory]\n%s\n" % ("\n".join(["  " + x for x in settings.factory.__str__().split("\n")]))
        r += self._cache.__str__()
        return r
