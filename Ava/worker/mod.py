import logging

from Ava.worker.cache import CacheWorker

logger = logging.getLogger(__name__)


class ModWorker(CacheWorker):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._mod_stack = []

    def get(self, tokens):
        if self._mod_stack:
            results = self._mod_stack[-1].get(tokens)
        else:
            results = super().get(tokens)
        return results
