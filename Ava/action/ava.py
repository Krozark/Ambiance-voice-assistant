import logging

from Ava.core import (
    Action
)

logger = logging.getLogger(__name__)


class AvaStopAction(Action):
    def _do_trigger(self, **kwargs) -> None:
        self.ava.stop()
