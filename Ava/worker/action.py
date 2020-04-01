import logging

from Ava.core import (
    IThread,
    Worker
)

logger = logging.getLogger(__name__)


class ActionWorker(Worker, IThread):
    def __init__(self, ava, **kwargs):
        Worker.__init__(self, ava, **kwargs)
        IThread.__init__(self)

    def _process_input_data(self, action) -> None:
        try:
            action.trigger()
        except Exception as e:
            logger.exception("Exception while trigger action %s", action, exc_info=e)
