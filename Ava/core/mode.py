import logging
from typing import List, Union, Dict

from .action import ActionList, Action
from .cache import CacheResult, Cache

logger = logging.getLogger(__name__)


class ModeResult:
    def __init__(self, len, action):
        self.length = len
        self.action = action

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


class Mode(object):
    def __init__(self, enter_tokens, enter_action, exit_tokens, exit_action):
        self._is_active = False
        self._enter_tokens = enter_tokens
        self._enter_action = enter_action
        self._exit_tokens = exit_tokens
        self._exit_action = exit_action
        self._node = Cache()

    def enter(self):
        self._is_active = True

    def exit(self):
        self._is_active = False

    def register(self, tokens: List[str], action: Union[Action, ActionList], token_regex: Dict[str, str] = None) -> None:
        return self._node.register(tokens, action, token_regex)

    def get(self, tokens) -> List:
        res = []
        if self._is_active is False:
            check = self._check_tokens(self._enter_tokens, tokens, self._enter_action)
            if check is not None:
                res.append(check)
        else:
            check = self._check_tokens(self._exit_tokens, tokens, self._exit_action)
            if check is not None:
                res.append(check)
            else:
                res = self._node.get(tokens)
        return res

    def _check_tokens(self, my_tokens, other_tokens, action):
        my_len = len(my_tokens)
        other_len = len(other_tokens)
        i = 0

        for i in range(0, min(my_len, other_len)):
            if my_tokens[i] != other_tokens[i]:
                return None
        if i == my_len:
            return ModeResult(i, action)
        return ModeResult(i, None)
