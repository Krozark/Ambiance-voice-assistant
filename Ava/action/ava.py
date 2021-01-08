import logging

from Ava.core import (
    Action
)

from Ava.settings import settings

logger = logging.getLogger(__name__)


class AvaStopAction(Action):
    def _do_trigger(self, **kwargs) -> None:
        settings.ava.stop()
