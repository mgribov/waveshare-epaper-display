import logging
from utility import get_json_from_url
from weather_providers.base_provider import BaseWeatherProvider


class WeatherGov(BaseWeatherProvider):
    def __init__(self, weathergov_self_id, location_lat, location_long, units):
        self.weathergov_self_id = weathergov_self_id
        self.location_lat = location_lat
        self.location_long = location_long
        self.units = units


    # Map weather.gov Icon URLs to icons
    # Reference https://api.weather.gov/icons and https://www.weather.gov/forecast-icons
    def get_icon_from_weathergov_icon_urls(self, icon_url, is_daytime):
        logging.debug(icon_url)
        # https://api.weather.gov/icons/land/day/sct/rain,30?size=medium --> sct
        weathergov_icon = icon_url.replace("https://","").split("/")[4].split(",")[0].split("?")[0]

        icon_dict = {
                    "skc": "clear_sky_day" if is_daytime else "clearnight",
                    "few": "few_clouds" if is_daytime else "partlycloudynight",
                    "sct": "scattered_clouds" if is_daytime else "partlycloudynight",
                    "bkn": "mostly_cloudy" if is_daytime else "mostly_cloudy_night",
                    "ovc": "overcast",
                    "wind_skc": "wind",
                    "wind_few": "wind",
                    "wind_sct": "wind",
                    "wind_bkn": "wind",
                    "wind_ovc": "wind",
                    "snow": "snow",
                    "rain_snow": "sleet",
                    "rain_sleet": "sleet",
                    "snow_sleet": "sleet",
                    "fzra": "climacell_freezing_rain",
                    "rain_fzra": "climacell_freezing_rain",
                    "snow_fzra": "climacell_freezing_rain",
                    "sleet": "sleet",
                    "rain": "climacell_rain_light" if is_daytime else 'rain_night_light',
                    "rain_showers": "climacell_rain" if is_daytime else "rain_night",
                    "rain_showers_hi": "day_partly_cloudy_rain" if is_daytime else "night_partly_cloudy_rain",
                    "tsra": "thundershower_rain",
                    "tsra_sct": "scattered_thundershowers",
                    "tsra_hi": "scattered_thundershowers",
                    "tornado": "tornado_hurricane",
                    "hurricane": "tornado_hurricane",
                    "tropical_storm": "tornado_hurricane",
                    "dust": "dust_ash_sand",
                    "smoke": "fire_smoke",
                    "haze": "haze",
                    "hot": "very_hot",
                    "cold": "cold",
                    "blizzard": "blizzard",
                    "fog": "climacell_fog"
                    }

        return icon_dict[weathergov_icon]

    def get_forecast_url(self, lat, long):
        logging.info("Using lat long to figure out the Weather.gov forecast URL")
        lookup_url = "https://api.weather.gov/points/{},{}".format(lat, long)
        lookup_data = get_json_from_url(lookup_url, {'User-Agent':'({0})'.format(self.weathergov_self_id)}, "cache_weather_gov_lookup.json", 3600)
        logging.debug(lookup_data)
        return lookup_data["properties"]["forecast"]

    # Get weather from Weather.Gov, US only
    # https://www.weather.gov/documentation/services-web-api
    def get_weather(self):

        forecast_url = self.get_forecast_url(self.location_lat, self.location_long)
        # https://api.weather.gov/gridpoints/TOP/31,80/forecast"
        logging.info(forecast_url)

        response_data = self.get_response_json(forecast_url, {'User-Agent':'({0})'.format(self.weathergov_self_id)})
        weather_data = response_data
        logging.debug("get_weather() - {}".format(weather_data))

        daytime = self.is_daytime(self.location_lat, self.location_long)

        # 2 periods per day
        periods_to_get = 6

        # {'number': 2, 'name': 'Tonight', 'startTime': '2022-03-06T18:00:00-06:00', 'endTime': '2022-03-07T06:00:00-06:00', 'isDaytime': False, 'temperature': 20, 'temperatureUnit': 'F', 'temperatureTrend': None, 'windSpeed': '10 to 15 mph', 'windDirection': 'N', 'icon': 'https://api.weather.gov/icons/land/night/snow,30/snow,20?size=medium', 'shortForecast': 'Chance Rain And Snow', 'detailedForecast': 'A chance of rain and snow before 3am. Mostly cloudy, with a low around 20. North wind 10 to 15 mph, with gusts as high as 25 mph. Chance of precipitation is 30%.'}

        weather = {}
        for period in range(0, periods_to_get):
            w = weather_data["properties"]["periods"][period]
            weather[period] = w

            weather[period]["icon"] = self.get_icon_from_weathergov_icon_urls(w["icon"], w['isDaytime'])

        logging.debug(weather)
        return weather
