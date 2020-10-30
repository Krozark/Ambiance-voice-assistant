import enum
import logging
import logging.config
import os

logger = logging.getLogger(__name__)

DEBUG = True
DEBUG_AUDIO_AS_TEXT = True

PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
DATA_PATH = os.path.join(PROJECT_PATH, "..", "data")


class TokenStrategy(enum.Enum):
    simple = 1
    lemma = 2
    stem = 3


class Settings(object):
    def __init__(self):
        self._languages = None
        self._current_language = None
        self._api_keys = None
        self.token_strategy = None
        self.clear()

    def clear(self):
        self._languages = {}
        self._current_language = None
        self._api_keys = {}
        self.token_strategy = TokenStrategy.simple

    def load(self, data):
        for key, value in data.items():
            logger.debug("Configure %s = %s", key, value)
            if key == "languages":
                self._current_language = value.pop("current")
                self._languages = value
            elif key == "api-keys":
                self._api_keys = value
            elif key == "logging":
                logging.config.dictConfig(value)
            else:
                self.set(key, value)

    @property
    def language_data(self):
        return self._languages.get(self._current_language, {})

    def set_language(self, lang):
        self._current_language = lang

    def set_language_data(self, lang, data):
        self._languages[lang] = data

    def api_key(self, key):
        return self._api_keys.get(key, None)

    def get(self, attr):
        return getattr(self, attr, None)

    def set(self, attr, value):
        setattr(self, attr, value)


settings = Settings()
