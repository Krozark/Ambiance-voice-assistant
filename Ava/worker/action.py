import logging
from Ava.core import (
    IThread,
)

logger = logging.getLogger(__name__)


class ActionWorker(IThread):
    def _process_input_data(self, action) -> None:
        try:
            action.trigger()
        except Exception as e:
            logger.exception("Exception while trigger action %s", action, exc_info=e)
