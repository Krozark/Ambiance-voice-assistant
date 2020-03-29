import logging

logger = logging.getLogger(__name__)


class Worker(object):
    def __init__(self, ava, **kwargs):
        self._ava = ava
        ava.add_worker(self)

    @property
    def ava(self):
        return self._ava