import logging

from pydub import AudioSegment
from pydub.playback import play

from Ava import config
from Ava.core import (
    Action
)

logger = logging.getLogger(__name__)


class AudioFilePlayerAction(Action):
    def __init__(self, ava, filename, *args, **kwargs):
        Action.__init__(self, ava, *args, name=filename, **kwargs)
        self._filename = filename

    def _do_trigger(self, **kwargs) -> None:
        if self.ava.config.get("audio_as_text"):
            logger.info("Play file %s", self._filename)
        else:
            audio = AudioSegment.from_file(self._filename)
            play(audio)


