import logging

from Ava.core import (
    ActionList
)
from Ava.core.mode import (
    ModeResult
)
from Ava.worker.cache import CacheWorker

logger = logging.getLogger(__name__)

class ModeWorker(CacheWorker):
    def __init__(self, ava, **kwargs):
        CacheWorker.__init__(self, ava, **kwargs)
        self._modes = []
        self._mode_stack = []

    def add_mode(self, mode):
        self._modes.append(mode)

    def get(self, tokens):
        if self._mode_stack:
            results = self._mode_stack[-1].get(self._tokens)
        else:
            results = []
            for mod in self._modes:
                results += mod.get(self._tokens)
            results += super().get(self._tokens)
            results = sorted(results)
        return results

    def _get_action(self, result):
        action = result.action
        action.set_trigger_kwargs(result.kwargs)
        if isinstance(result, ModeResult):
            result.mode.toggle(self._mode_stack)
        return action
