import logging
from Ava.settings import settings


logger = logging.getLogger(__name__)


class Worker(object):
    def __init__(self, **kwargs):
        settings.ava.add_worker(self)
