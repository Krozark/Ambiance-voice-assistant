import logging

from meteofrance.client import meteofranceClient, meteofranceError

from Ava.core import (
    Action,
    TTSMixin
)

logger = logging.getLogger(__name__)


class WeatherAction(Action, TTSMixin):
    def __init__(self, ava, *args, city=None, day=0, **kwargs):
        Action.__init__(self, ava, *args, **kwargs)
        self._city = city
        self._day = day

    def _do_trigger(self, *args, city=None, day=0, **kwargs) -> None:
        city = city or self._city
        day = day or self._day
        try:
            client = meteofranceClient(city, True, include_today=True)
            data = client.get_data()
            logger.debug("Weather data for city=%s day=%s: %s", city, day, data)
            day_str= "aujourd'hui" if day==0 else "dans %s jours" % day
            msg = "La météo à %s pour %s. " % (data["name"], day_str)
            weather = data["forecast"][day]
            if day == 0:
                msg += "Le temps est %s et la température %s" % (
                    data["weather"],
                    data["temperature"]
                )
            else:
                msg += weather["weather"]

            msg +=" avec des température allant de %s à %s." % (
                weather["min_temp"],
                weather["max_temp"]
            )
        except meteofranceError:
            logger.error("Impossible to get weather for city=%s, day=%s", city, day)
            msg = "impossible to get weather informations"

        self.say(msg)
