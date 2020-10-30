from .proxy import ProxyClass
from .facades.stt import RecognizerFacade

STTRecognizer = ProxyClass(RecognizerFacade)

