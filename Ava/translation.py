import gettext
import logging

logger = logging.getLogger(__name__)


class Translator(object):
    trans = None

    def set_language(self, localedir, lang):
        logger.info("Loading language %s from %s", lang, localedir)
        self.trans = gettext.translation("ava", localedir=localedir, languages=[lang, ])

    def translate(self, *args, **kwargs):
        return self.trans.gettext(*args, **kwargs)


translator = Translator()
_ = translator.translate
