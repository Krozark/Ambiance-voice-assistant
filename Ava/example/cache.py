import logging
import os

from Ava import config
from Ava.action import (
    AudioFilePlayerAction
)
from Ava.core import (
    Cache,
    CallbackAction
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

cache = Cache()
tokens = "Le Mystère des XV est un roman français de Jean de La Hire publié en feuilleton en 1911 dans le quotidien Le Matin.".split()

slice = "est un roman français".split()
action = CallbackAction(lambda: logger.info("Action: est un roman français"), name="est un roman français")
cache.register(slice, action)

slice = "est un roman".split()
action = AudioFilePlayerAction(os.path.join(config.DATA_PATH, "Splash-Ploor.mp3"), name="est un roman")
cache.register(slice, action)

logger.debug("Cache:\n %s", cache)

while len(tokens):
    logger.debug("Search action for '%s'", " ".join(tokens))
    index, action = cache.get(tokens)
    if not index:
        tokens = tokens[1:]
    else:
        logger.debug("Action '%s' found with index %s", action, index)
        action.trigger()
        tokens = tokens[index:]

logger.debug("Search action for 'est un roman anglais'")
index, action = cache.get("est un roman anglais".split())
action.trigger()
