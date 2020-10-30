import logging
import re
from meteofrance.client import meteofranceClient, meteofranceError

from Ava.core import (
    Action,
    TTSMixin
)

logger = logging.getLogger(__name__)


def day_to_int(day, data):
    if isinstance(day, int):
        return day
    res = 0
    if day == "demain":
        res = 1
    elif day == "après demain":
        res = 2
    else:
        m = re.match("dans (\d)+ jour[s]?", day)
        if m:
            res = int(m.group(1))
        else:
            d = day[:3]
            for key, value in data.items():
                if value["date"][:3] == d:
                    res = key
                    break
    return res


class WeatherAction(Action, TTSMixin):
    def __init__(self, *args, city=None, day=0, **kwargs):
        Action.__init__(self, *args, **kwargs)
        self._city = city
        self._day = day

    def _do_trigger(self, *args, city=None, day=0, **kwargs) -> None:
        city = city or self._city
        try:
            client = meteofranceClient(city, True, include_today=True)
            data = client.get_data()
            day = day_to_int(day or self._day, data["forecast"])
            logger.debug("Weather data for city=%s day=%s: %s", city, day, data)
            day_str= "aujourd'hui" if day == 0 else "dans %s jours" % day

            msg = "La météo à %s pour %s. " % (data["name"], day_str)
            weather = data["forecast"][day]

            if day == 0:
                msg += "Le temps est %s et la température %s" % (
                    data["weather"],
                    data["temperature"]
                )
                if "rain_forecast_text" in data:
                    msg += ". " + data["rain_forecast_text"]
            else:
                msg += weather["weather"]

            msg +=" avec des température allant de %s à %s." % (
                weather["min_temp"],
                weather["max_temp"]
            )
        except Exception as e:
            logger.exception("Impossible to get weather for city=%s, day=%s", city, day, exc_info=e)
            msg = "impossible to get weather informations"

        self.say(msg)
