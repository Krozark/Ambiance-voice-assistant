from espeakng import ESpeakNG


class TTSEngine:
    def __init__(self):
        self._engine = self._get_engine()

    def _get_engine(self):
        engine = ESpeakNG()
        engine.voice = "fr"
        engine.pitch = 32
        engine.speed = 150
        return engine

    def say(self, text):
        self._engine.say(text)
