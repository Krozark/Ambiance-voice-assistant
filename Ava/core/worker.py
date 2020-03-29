import logging

from .common import WithAva

logger = logging.getLogger(__name__)


class Worker(WithAva):
    def __init__(self, ava, **kwargs):
        WithAva.__init__(self, ava)
