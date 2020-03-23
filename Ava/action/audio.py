import logging

from pydub import AudioSegment
from pydub.playback import play

from Ava import config
from Ava.core import (
    Action
)

logger = logging.getLogger(__package__)


class AudioFilePlayerAction(Action):
    def __init__(self, filename, *args, **kwargs):
        self._filename = filename
        kwargs.setdefault("name", filename)
        super().__init__(*args, **kwargs)

    def trigger(self) -> None:
        if config.DEBUG_AUDIO_AS_TEXT:
            logger.info("Play file %s", self._filename)
        else:
            audio = AudioSegment.from_file(self._filename)
            play(audio)


