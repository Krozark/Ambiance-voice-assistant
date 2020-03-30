import logging
from typing import List, Union, Dict

from .action import ActionList, Action
from .cache import (
    CacheResult,
    Cache,
    CacheNodeData
)
from .utils import get_register

logger = logging.getLogger(__name__)


class ModResult:
    def __init__(self, len, action, mod):
        self.length = len
        self.action = action
        self.mod = mod
        self.kwargs = {}

    def if_deeper(self):
        return self.action is None

    def __gt__(self, other):
        if other is None:
            return True

        if isinstance(other, CacheResult):
            return True

        if other.length < self.length:
            return True
        elif other.length == self.length:
            if self.if_deeper() == other.if_deeper():
                return self.if_deeper()
        return False

    def __str__(self):
        return "length=%s, action=%s, mod=%s" % (self.length, self.action, self.mod)


class Mod(CacheNodeData):
    def __init__(self, ava, enter, exit):
        CacheNodeData.__init__(self)
        self._is_active = False
        self.regex_kwargs = dict()

        if not isinstance(enter, (list, tuple)):
            enter = [enter]
        enter_action, enter_tokens, enter_regex, enter_data = get_register(ava, enter)[0]

        if not isinstance(exit, (list, tuple)):
            exit = [exit]
        #exit_action, exit_tokens, exit_regex, exit_data = get_register(ava, [exit])[0]

    def toggle(self, seq=None):
        self._is_active = not self._is_active
        if seq:
            if self._is_active:
                logger.debug("Entering in Mode %s", self._enter_tokens)
                seq.append(self)
            else:
                logger.debug("Exiting mod %s", self._enter_tokens)
                seq.pop()

    # def register(self, tokens: List[str], action: Union[Action, ActionList], token_regex: Dict[str, str] = None) -> None:
    #     return self._node.register(tokens, action, token_regex)

    def get(self, tokens, depth=0, kwargs=None, results=None) -> List:
        results = results or []
        kwargs = kwargs or {}
        if self._is_active is False:
            check = self._check_tokens(self._enter_tokens, tokens, self._enter_action)
            if check is not None:
                res = [check]
        else:
            check = self._check_tokens(self._exit_tokens, tokens, self._exit_action)
            if check is not None:
                res = [check]
            else:
                res = super().get(tokens)
        return results

    def _check_tokens(self, my_tokens, other_tokens, action):
        my_len = len(my_tokens)
        other_len = len(other_tokens)
        i = 0
        while i < min(my_len, other_len):
            if my_tokens[i] != other_tokens[i]:
                return None
            i += 1

        if i == my_len:
            return ModResult(i, action, self)
        return ModResult(i, None, self)

    def __str__(self, depth=0):
        r = "  " * depth + "[Mod]\n"
        r += super().__str__(depth=depth + 1)
        return r
