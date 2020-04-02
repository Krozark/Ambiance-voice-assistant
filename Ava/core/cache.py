import logging
import re
from collections import defaultdict
from typing import List, Union, Dict

from .action import ActionList, Action

logger = logging.getLogger(__name__)


class CacheResult(object):
    def __init__(self, length, action, kwargs):
        self.length = length
        self.action = action
        self.kwargs = kwargs

    def if_deeper(self):
        return self.action is None

    def __gt__(self, other):
        """
        Sort by:
        length, deeper, len(kwargs)
        :param other:
        :return:
        """
        if other is None:
            return True

        if not isinstance(other, CacheResult):
            return False

        if other.length < self.length:
            return True
        elif other.length == self.length:
            if self.if_deeper() == other.if_deeper():
                if len(self.kwargs) < len(other.kwargs):
                    return True
            else:
                return self.if_deeper()
        return False

    def __str__(self):
        return "length=%s, action=%s, regex=%s" % (self.length, self.action, self.kwargs.items())


class _RegexNodeStruct(object):
    def __init__(self, name, regex_data, node):
        self.name = name
        self.node = node
        if isinstance(regex_data, str):
            self.regex_str = regex_data
            self.regex_multiple = False
        else:
            self.regex_str = regex_data["regex"]
            self.regex_multiple = regex_data.get("multiple", False)
        self._regex_compiled = re.compile(self.regex_str)

    def match(self, token):
        return re.match(self._regex_compiled, token)

    def __str__(self, depth=0):
        r = "%s(%s)" % (self.name, self.regex_str)
        if self.regex_multiple:
            r += "*"
        return r


class CacheNodeData(object):
    def __init__(self):
        self._leaf = ActionList()
        self._nodes = dict()
        self._node_regex = list()  # (_RegexNodeStruct),

    def can_deeper(self):
        return bool(len(self._nodes) + len(self._node_regex))

    def get(self, tokens: List[str], depth, kwargs, results: List[CacheResult]) -> None:
        if tokens:
            # try to found deeper
            token = tokens[0]
            try:
                self._nodes[token].get(tokens[1:], depth + 1, kwargs, results)
            except KeyError:
                pass

            for regex_struct in self._node_regex:
                if regex_struct.match(token):
                    copy = kwargs.copy()
                    copy[regex_struct.name].append(token)
                    regex_struct.node.get(tokens[1:], depth + 1, copy, results)
                    if regex_struct.regex_multiple:
                        self.get(tokens[1:], depth + 1, copy, results)

        elif self.can_deeper():
            # no more token, but we can potentially match if mor token received
            results.append(CacheResult(depth, None, kwargs))

        if self._leaf:
            # We have a leaf, to we add it
            results.append(CacheResult(depth, self._leaf, kwargs))

    def register(self, tokens: List[str], action: Union[Action, ActionList], token_regex: Dict[str, str]) -> None:
        if not tokens:
            assert isinstance(action, (ActionList, Action))
            self._leaf.append(action)
        else:
            token = tokens[0]
            replace = False
            if len(tokens) == 1 and isinstance(action, CacheNodeData):
                replace = True

            if token not in token_regex:
                if replace:
                    node = self._nodes.get(token)
                    action.merge(node)
                    self._nodes[token] = action
                else:
                    self._nodes.setdefault(token, CacheNodeData())
                node = self._nodes.get(token)
            else:
                for regex_struct in self._node_regex:
                    if regex_struct.name == token:
                        node = regex_struct.node
                        if replace:
                            action.merge(node)
                            regex_struct.node = action
                            node = action
                        break
                else:
                    new = action if replace else CacheNodeData()
                    self._node_regex.append(_RegexNodeStruct(token, token_regex[token], new))
                    node = self._node_regex[-1].node

            if not replace:
                node.register(tokens[1:], action, token_regex)

    def merge(self, other):
        if other is None:
            return
        assert isinstance(other, CacheNodeData)
        self._leaf += other._leaf
        self._nodes.update(other._nodes)
        self._node_regex += other._node_regex

    def __str__(self, depth=0):
        r = ""
        if self._leaf:
            for x in self._leaf.__str__().split("\n"):
                r += "  " * depth + "[Action] %s \n" % x

        for key, value in self._nodes.items():
            r += "  " * depth + "[Node] %s \n" % key
            r += value.__str__(depth + 1)

        for regex_struct in self._node_regex:
            r += "  " * depth + "[Node Regex] %s \n" % regex_struct
            r += regex_struct.node.__str__(depth + 1)
        return r


class Cache(object):
    def __init__(self):
        self._root = CacheNodeData()

    def register(self, tokens: List[str], action: Union[Action, ActionList, CacheNodeData], token_regex: Dict[str, str]=None) -> None:
        assert isinstance(action, (Action, ActionList, CacheNodeData))
        token_regex = token_regex or dict()
        logger.debug("Register tokens '%s' to '%s', token_regex=%s", tokens, action, token_regex)
        self._root.register(tokens, action, token_regex)

    def get(self, tokens) -> List[CacheResult]:
        results = []
        kwargs = defaultdict(list)
        self._root.get(tokens, 0,  kwargs, results)
        return results

    def __str__(self, depth=0):
        return "  " * depth + self._root.__str__(depth=depth)
