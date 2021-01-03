import logging
from Ava.settings import settings


logger = logging.getLogger(__name__)


def get_tokens(tokens):
    token_regex = dict()
    if isinstance(tokens, dict):
        token_regex = tokens.get("regex") or token_regex
        tokens = tokens.get("tokens", "")
    # normalize tokens
    if isinstance(tokens, str):
        tokens = [tokens]
    res = []
    for sentence in tokens:
        if isinstance(sentence, str):
            sentence = settings.ava.tokenize(sentence)
        res.append([x.lower() for x in sentence])
    return res, token_regex


def get_register(data_list):
    from Ava.core.action import ActionList
    res = []
    for data in data_list:
        logger.debug("Parsing data: %s", data)
        # get object
        type_type = data["type"]
        if isinstance(type_type, list):
            obj = ActionList()
            for t in type_type:
                args = []
                kwargs = None
                if isinstance(t, dict):
                    type_args = t.get("args", None)
                    if type_args is not None:
                        if isinstance(type_args, (list, tuple)):
                            args += type_args
                        else:
                            args.append(type_args)
                    kwargs = t.get("kwargs", None)
                    t = t["type"]
                obj.append(
                    settings.factory.construct(t, args=args, kwargs=kwargs)
                )
        else:
            args = []
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
            obj = settings.factory.construct(type_type, args=args, kwargs=kwargs)

        # tokens
        tokens_sentences, token_regex = get_tokens(data.get("tokens", ""))
        res.append((obj, tokens_sentences, token_regex, data))
    return res


def load_register(data_list, target):
    for obj, tokens_sentences, token_regex, data in get_register(data_list):
        logger.debug("obj=%s, tokens_sentences=%s, token_regex=%s, data=%s", obj, tokens_sentences, token_regex, data)
        # recurse if needed
        other = data.get("register", [])
        if other:
            load_register(other, obj)
        # register
        for tokens in tokens_sentences:
            target.register(tokens, obj, token_regex=token_regex)