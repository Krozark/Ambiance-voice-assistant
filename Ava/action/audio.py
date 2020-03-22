from pydub import AudioSegment
from pydub.playback import play

from .base import Action


class AudioFilePlayerAction(Action):
    def __init__(self, filename, *args, **kwargs):
        self._filename = filename
        kwargs.setdefault("name", filename)
        super().__init__(*args, **kwargs)

    def trigger(self) -> None:
        audio = AudioSegment.from_file(self._filename)
        play(audio)


