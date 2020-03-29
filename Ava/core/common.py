import logging

logger = logging.getLogger(__name__)


class WithAva(object):
    def __init__(self, ava):
        self._ava = ava

    @property
    def ava(self):
        return self._ava