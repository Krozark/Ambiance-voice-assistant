import logging

logger = logging.getLogger(__name__)


class WithAva(object):
    def __init__(self, ava):
        self._ava = ava

    @property
    def ava(self):
        return self._ava


def get_register(ava, data_list):
    res = []
    for data in data_list:
        logger.debug("Parsing data: %s", data)
        # get object
        type_type = data["type"]
        args = [ava]
        kwargs = None
        if isinstance(type_type, dict):
            type_args = type_type.get("args", None)
            if type_args is not None:
                if isinstance(type_args, (list, tuple)):
                    args += type_args
                else:
                    args.append(type_args)
            kwargs = type_type.get("kwargs", None)
            type_type = type_type["type"]
        obj = ava._factory.construct(type_type, args=args, kwargs=kwargs)

        # tokens
        tokens_tokens = data["tokens"]
        token_regex = dict()
        if isinstance(tokens_tokens, dict):
            token_regex = tokens_tokens.get("regex") or token_regex
            tokens_tokens = tokens_tokens.get("tokens", {})
        # normalize tokens
        if isinstance(tokens_tokens, str):
            tokens_tokens = ava.tokenize(tokens_tokens)
        if isinstance(tokens_tokens, (tuple, list)):
            tokens_tokens = [x.lower() for x in tokens_tokens]

        res.append((obj, tokens_tokens, token_regex, data))
    return res

def load_register(ava, data_list, target):
    for obj, tokens, token_regex, data in get_register(ava, data_list):
        # recurse if needed
        other = data.get("register", [])
        if other:
            load_register(ava, other, obj)
        # register
        target.register(tokens, obj, token_regex=token_regex)