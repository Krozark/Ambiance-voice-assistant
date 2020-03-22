import logging
from typing import List, Tuple

from Ava.utils.action import Action, ActionList


logger = logging.getLogger(__package__)


class _CacheNodeData(object):
    def __init__(self):
        self._leaf = ActionList()
        self._nodes = dict()

    def get(self, tokens: List[str], depth):
        if not tokens:
            if self._leaf:
                return depth, self._leaf
        else:
            try:
                return self._nodes[tokens[0]].get(tokens[1:], depth + 1)
            except KeyError:
                if self._leaf:
                    return depth, self._leaf

        return 0, None

    def register(self, tokens, action):
        if tokens:
            self._nodes.setdefault(tokens[0], _CacheNodeData())
            node = self._nodes.get(tokens[0])
            node.register(tokens[1:], action)
        else:
            self._leaf.append(action)

    def __str__(self, depth=0):
        r = ""
        if self._leaf:
            for x in self._leaf.__str__().split("\n"):
                r += "  " * depth + "[Action] %s \n" % x

        for key, value in self._nodes.items():
            r += "  " * depth + "[Node] %s \n" % key
            r += value.__str__(depth + 1)
        return r


class Cache(object):
    def __init__(self):
        self._root = _CacheNodeData()

    def register(self, tokens, action) -> None:
        logger.debug("Register '%s' to action '%s'", tokens, action)
        self._root.register(tokens, action)

    def get(self, tokens) -> Tuple[int, Action]:
        return self._root.get(tokens, 0)

    def __str__(self):
        return self._root.__str__()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    cache = Cache()
    tokens = "Le Mystère des XV est un roman français de Jean de La Hire publié en feuilleton en 1911 dans le quotidien Le Matin.".split()

    slice = "est un roman français".split()
    action = Action(lambda: logger.info("Action: est un roman français"), "est un roman français")
    cache.register(slice, action)

    slice = "est un roman".split()
    action = Action(lambda: logger.info("Action: est un roman"), "est un roman")
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