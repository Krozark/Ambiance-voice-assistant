import logging
import re

from meteofrance_api import MeteoFranceClient
import datetime
from Ava.core import (
    Action,
    TTSMixin
)

from Ava.translation import _

logger = logging.getLogger(__name__)


class WeatherAction(Action, TTSMixin):
    def __init__(self, *args, city=None, day=0, **kwargs):
        Action.__init__(self, *args, **kwargs)
        self._city = city
        self._day = day

    def _do_trigger(self, *args, city=None, day=0, **kwargs) -> None:
        print(_)
        city = city or self._city
        logger.debug("Weather data for city=%s day=%s", city, day)
        try:
            client = MeteoFranceClient()
            list_places = client.search_places(city)
            my_place = list_places[0]
            my_place_weather_forecast = client.get_forecast_for_place(my_place)
            day_delta = self.day_to_int(day or self._day, my_place_weather_forecast)

            day_str = _("today") if day_delta == 0 else _("in %s days") % day_delta
            weather = ""
            temperature = ""
            rain_status = ""
            alert = ""

            # special case for today
            if day_delta == 0:
                forecast = my_place_weather_forecast.current_forecast
                weather = forecast["weather"]["desc"].lower()
                temperature = _("a temperature of %s") % forecast["T"]["value"]

                # If rain in the hour forecast is available, get it.
                if my_place_weather_forecast.position["rain_product_available"] == 1:
                    my_place_rain_forecast = client.get_rain(my_place.latitude, my_place.longitude)
                    next_rain_dt = my_place_rain_forecast.next_rain_date_locale()
                    if next_rain_dt:
                        rain_status = next_rain_dt.strftime(_("rain forecast at %H hour %M minutes "))

                department = my_place_weather_forecast.position["dept"]
                try:
                    alert = client.get_warning_full(department).raw_data["comments"]["text_bloc_item"][0]["text"]
                except:
                    pass

            else:
                forecast = my_place_weather_forecast.daily_forecast[day_delta]
                weather = forecast["weather12H"]["desc"].lower()
                temperature = _("temperatures from %s to %s") % (
                    forecast["T"]["min"],
                    forecast["T"]["max"]
                )

            msg = _("Weather forcast at {city} for {day}. {weather} with {temperature} {rain} {alert}.").format(
                city=city,
                day=day_str,
                weather=weather,
                temperature=temperature,
                rain=rain_status,
                alert=alert
            )

        except Exception as e:
            logger.exception("Impossible to get weather for city=%s, day=%s", city, day, exc_info=e)
            msg = _("impossible to get weather informations")
        logger.debug(msg)
        self.say(msg)

    def day_to_int(self, day, data):
        if isinstance(day, int):
            return day

        res = 0

        m = re.match(_("in (?P<day>[\d]+) day[s]?"), day)
        if m:
            tmp = int(m.groupdict()["day"])
            if tmp < len(data):
                res = tmp
        else:
            day_cycle = self.get_day_cycle()
            m = re.match(_("(for )?(?P<next>next )?(?P<day>[\w]+)"), day)
            if m:
                day = m.groupdict()["day"]
                logger.debug("day = %s", day)
                today = datetime.date.today().weekday()  # index of today
                if day in day_cycle:
                    day_index = day_cycle.index(day)  # index of the request day
                    res = (today - day_index) % (len(day_cycle) + 1)  # compute the delta
                    if m.groupdict()["next"]:  # add a week if needed
                        res += len(day_cycle)
                else:
                    day_to_int_map = self.get_day_to_int_map()
                    if day in day_to_int_map.keys():
                        res = day_to_int_map[day]
        return res

    def get_day_to_int_map(self):
        return {
            _("today"): 0,
            _("tomorrow"): 1,
            _("after tomorrow"): 2
        }

    def get_day_cycle(self):
        return [
            _("monday"),
            _("tuesday"),
            _("wednesday"),
            _("thursday"),
            _("friday"),
            _("saturday"),
            _("sunday")
        ]
