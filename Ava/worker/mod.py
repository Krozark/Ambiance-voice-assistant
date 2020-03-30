import logging

from Ava.core import (
    ActionList
)
from Ava.core.mod import (
    ModResult
)
from Ava.worker.cache import CacheWorker

logger = logging.getLogger(__name__)


class ModWorker(CacheWorker):
    def __init__(self, ava, **kwargs):
        CacheWorker.__init__(self, ava, **kwargs)
        self._mods = []
        self._mod_stack = []

    def add_mod(self, mod):
        self._mods.append(mod)

    def get(self, tokens):
        if self._mod_stack:
            results = self._mod_stack[-1].get(self._tokens)
        else:
            results = []
            for mod in self._mods:
                results += mod.get(self._tokens)
            results += super().get(self._tokens)
            results = sorted(results)
        return results

    def _get_action(self, result):
        action = result.action
        action.set_trigger_kwargs(result.kwargs)
        if isinstance(result, ModResult):
            result.mod.toggle(self._mod_stack)
        return action
