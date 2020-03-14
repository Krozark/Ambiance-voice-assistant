import logging
from Ava.stem import steam_sentence


logger = logging.getLogger(__package__)

logging.basicConfig(level=logging.DEBUG)


class _WithName:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

class Event(_WithName):
    def trigger(self):
        print("Trigger event <%s>" % self.name)

class EventList:
    def __init__(self):
        self._events = []

    def add(self, event):
        assert isinstance(event, Event)
        self._events.append(event)

    def trigger(self):
        for e in self._events:
            e.trigger()

    def display(self, tab=0):
        for e in self._events:
            print("%s[Event] <%s>" % ("\t" * tab, e))

    def __bool__(self):
        return self._events.__bool__()

class _CacheNode(_WithName):
    def __init__(self, *args):
        super().__init__(*args)
        self._leaf = EventList()
        self._nodes = {} # str, _CacheNode

    def display(self, tab=0):
        print("%s [Node] <%s>" % ("\t" * tab, self.name))
        self._leaf.display(tab + 1)
        for k, v in self._nodes.items():
            v.display(tab + 1)

    def add(self, tokens, event):
        logger.debug("Add tokens %s", tokens)
        if not tokens:
            logger.debug("Associate event <%s>", event)
            self._leaf.add(event)
        else:
            token = tokens[0]
            self._nodes.setdefault(token, _CacheNode(token))
            self._nodes[token].add(tokens[1:], event)

    def get(self, tokens):
        if not tokens:
            return self._leaf
        try:
            token = tokens[0]
            return self._nodes[token].get(tokens[:1])
        except KeyError:
            logger.debug("No key %s", token)
            logger.debug(self._nodes.keys())
            return EventList()

class Cache:
    def __init__(self):
        self._root = {}

    def add(self, sentence, event):
        assert sentence
        tokens = list(steam_sentence(sentence))
        logger.debug("Add tokens: %s", tokens)
        token = tokens[0]
        self._root.setdefault(token, _CacheNode(token))
        self._root[token].add(tokens[1:], event)

    def get(self, sentence):
        assert sentence
        tokens = list(steam_sentence(sentence))
        token = tokens[0]
        try:
            return self._root[token].get(tokens[1:])
        except KeyError:
            logger.debug("No key %s", token)
            return EventList()

    def display(self):
        for k, v in self._root.items():
            v.display()




cache = Cache()
cache.add("la nuit tombe", Event("la nuit tombe"))
cache.add("la nuit se lève", Event("la nuit se lève"))
cache.display()
print(cache.get("la nuit tombe"))
print(cache.get("la nuit se lève"))
print(cache.get("la journée est belle"))
print(cache.get("le jour est beau"))