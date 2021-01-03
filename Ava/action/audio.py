import logging
import random
from sound_player import Sound

from Ava.core import (
    Action
)
from Ava.settings import settings

logger = logging.getLogger(__name__)


class AudioFilePlayerAction(Action):
    def __init__(self, filename, *args, playlist=None, loop=None, **kwargs):
        filenames = [filename, *args]
        Action.__init__(self, name=", ".join(filenames), **kwargs)
        self._filenames = filenames
        self._playlist = playlist
        self._loop = loop

    def _do_trigger(self, playlist=None, loop=None, **kwargs) -> None:
        playlist = playlist or self._playlist
        loop = loop or self._loop
        filename = random.choice(self._filenames)
        if settings.get("audio_as_text"):
            logger.info("Play file %s to playlist %s", filename, playlist)
        else:
            sound = Sound(filename)
            if loop != 1:
                sound.set_loop(loop)
            settings.ava._player.enqueue(sound, playlist)  # TODO


class AudioStopAction(Action):
    def __init__(self, playlist=None, **kwargs):
        super().__init__(name=playlist, **kwargs)
        self._playlist = playlist

    def _do_trigger(self, playlist=None, **kwargs) -> None:
        playlist = playlist or self._playlist
        if settings.get("audio_as_text"):
            logger.info("Stop playlist %s", playlist)
        else:
            settings.ava._player.stop(playlist=playlist)

