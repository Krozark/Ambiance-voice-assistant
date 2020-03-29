import os

DEBUG = True
DEBUG_AUDIO_AS_TEXT = False

PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
DATA_PATH = os.path.join(PROJECT_PATH, "..", "data")

LANGUAGES_INFORMATION = {
    "fr": {
        "recognition": "fr-FR",
        "voice": "french-mbrola-4",
        "nltk": "french",
        "input-file": os.path.join(DATA_PATH, "text-francais-utf8.txt"),
        "spacy": "fr_core_news_md",
        "data-file": os.path.join(DATA_PATH, "data.json"),
        "wikipedia": "fr"
    }
}
LANGUAGE_CURRENT = "fr"
LANGUAGES_INFORMATION_CURRENT = LANGUAGES_INFORMATION[LANGUAGE_CURRENT]

GOOGLE_RECOGNITION_KEY = None
