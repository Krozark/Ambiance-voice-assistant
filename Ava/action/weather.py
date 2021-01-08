import logging
import re

from meteofrance_api import MeteoFranceClient
import datetime
from Ava.core import (
    Action,
    TTSMixin
)

logger = logging.getLogger(__name__)

day_to_int_map = {
    "aujourd'hui": 0,
    "demain": 1,
    "après-demain": 2
}

day_cycle = [
    "lundi",
    "mardi",
    "mercredi",
    "jeudi",
    "vendredi",
    "samedi",
    "dimanche"
]


def day_to_int(day, data):
    if isinstance(day, int):
        return day
    res = 0

    m = re.match("dans (\d+) jour[s]?", day)
    if m:
        tmp = int(m.group(1))
        if tmp < len(data):
            res = tmp
    else:
        m = re.match("((le|de|pour) )?([-\w]+)( prochain)?", day)
        if m:
            day = m.group(3)
            today = datetime.date.today().weekday()  # index of today
            if day in day_cycle:
                day_index = day_cycle.index(day)  # index of the request day
                res = (today - day_index) % (len(day_cycle) + 1)  # compute the delta
                if m.group(4):  # add a week if needed
                    res += len(day_cycle)
            elif day in day_to_int_map.keys():
                res = day_to_int_map[day]
    return res


class WeatherAction(Action, TTSMixin):
    def __init__(self, *args, city=None, day=0, **kwargs):
        Action.__init__(self, *args, **kwargs)
        self._city = city
        self._day = day

    def _do_trigger(self, *args, city=None, day=0, **kwargs) -> None:
        city = city or self._city
        logger.debug("Weather data for city=%s day=%s", city, day)
        try:
            client = MeteoFranceClient()
            list_places = client.search_places(city)
            my_place = list_places[0]
            my_place_weather_forecast = client.get_forecast_for_place(my_place)
            day_delta = day_to_int(day or self._day, my_place_weather_forecast)

            day_str = "aujourd'hui" if day_delta == 0 else "dans %s jours" % day_delta
            weather = ""
            temperature = ""
            rain_status = ""
            alert = ""

            # special case for today
            if day_delta == 0:
                forecast = my_place_weather_forecast.current_forecast
                weather = forecast["weather"]["desc"].lower()
                temperature = "une température de %s" % forecast["T"]["value"]

                # If rain in the hour forecast is available, get it.
                if my_place_weather_forecast.position["rain_product_available"] == 1:
                    my_place_rain_forecast = client.get_rain(my_place.latitude, my_place.longitude)
                    next_rain_dt = my_place_rain_forecast.next_rain_date_locale()
                    if next_rain_dt:
                        rain_status = "Pluie prévue à " + next_rain_dt.strftime("%H heure %M minutes ")

                department = my_place_weather_forecast.position["dept"]
                try:
                    alert = client.get_warning_full(department).raw_data["comments"]["text_bloc_item"][0]["text"]
                except:
                    pass

            else:
                forecast = my_place_weather_forecast.daily_forecast[day_delta]
                weather = forecast["weather12H"]["desc"].lower()
                temperature = "des températures allant de %s à %s" % (
                    forecast["T"]["min"],
                    forecast["T"]["max"]
                )

            msg = "Météo à {city} pour {day}. {weather} avec {temperature} {rain} {alert}.".format(
                city=city,
                day=day_str,
                weather=weather,
                temperature=temperature,
                rain=rain_status,
                alert=alert
            )

        except Exception as e:
            logger.exception("Impossible to get weather for city=%s, day=%s", city, day, exc_info=e)
            msg = "impossible to get weather informations"

        self.say(msg)
