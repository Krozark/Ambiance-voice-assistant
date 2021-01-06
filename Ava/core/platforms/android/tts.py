import logging
from time import sleep

from jnius import autoclass

from Ava.core.facades.tts import TTSFacade
from Ava.core.platforms.android import activity
from Ava.settings import settings

logger = logging.getLogger(__name__)

Locale = autoclass('java.util.Locale')
TextToSpeech = autoclass('android.speech.tts.TextToSpeech')


class AndroidTTSEngine(TTSFacade):
    def __init__(self):
        super().__init__()
        lang = settings.language_data.get["tts"]
        local = getattr(Locale, lang)

        self._engine = TextToSpeech(activity, None)
        self._engine.setLanguage(local)

    def _say(self, text, sync=False) -> None:
        retries = 0  # First try rarely succeeds due to some timing issue
        speak_status = self.tts.speak(
                text,
                TextToSpeech.QUEUE_FLUSH,
                None
        )
        while retries < 100 and speak_status == -1:
            sleep(0.1)
            speak_status = self.tts.speak(
                text,
                TextToSpeech.QUEUE_FLUSH,
                None
            )


def instance_class():
    return AndroidTTSEngine
