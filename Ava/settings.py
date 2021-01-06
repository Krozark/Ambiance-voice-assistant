import enum
import logging
import logging.config
import os

from Ava.core.factory import Factory
from Ava.core.platform import platform as sys_platform


logger = logging.getLogger(__name__)

DEBUG = True
DEBUG_AUDIO_AS_TEXT = True

PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
DATA_PATH = os.path.abspath(os.path.join(PROJECT_PATH, "..", "data"))
LANG_PATH = os.path.join(DATA_PATH, "lang")
MODEL_DIRNAME = "model"

AVA_JSON_PATH = os.path.join(DATA_PATH, "ava.json")
REGISTER_FILENAME = "register.json"

AUDIO_RATE = 16000
AUDIO_CHUNK = 8000
AUDIO_CHANNELS = 1


class TokenStrategy(enum.Enum):
    simple = 1
    lemma = 2
    stem = 3


class Settings(object):
    def __init__(self):
        self._languages = None
        self._current_language = None
        self.token_strategy = None
        self.ava = None
        self.factory = Factory()
        self.clear()

    def clear(self):
        self._languages = {}
        self._current_language = None
        self.token_strategy = TokenStrategy.simple

    def load(self, data):
        for key, value in data.items():
            logger.debug("Configure %s = %s", key, value)
            if key == "languages":
                self._current_language = value.pop("current")
                self._languages = self._parse_platform(value)
                logger.debug(self._languages)
            elif key == "logging":
                logging.config.dictConfig(value)
            else:
                self.set(key, value)

    @property
    def language_data(self):
        return self._languages.get(self._current_language, {})

    def get_language(self):
        return self._current_language

    def set_language(self, lang):
        self._current_language = lang

    def set_language_data(self, lang, data):
        self._languages[lang] = data

    def get(self, attr):
        return getattr(self, attr, None)

    def set(self, attr, value):
        setattr(self, attr, value)

    def _parse_platform(self, data):
        if isinstance(data, dict):
            platform_value = data.pop("_platform", None)
            if platform_value:
                for key, value in platform_value.get(sys_platform, {}).items():
                    data[key] = value

            for key in data.keys():
                data[key] = self._parse_platform(data[key])

        return data

settings = Settings()