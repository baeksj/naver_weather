"""Support for Naver Weather Sensors."""
from datetime import timedelta
import logging

from homeassistant.components.weather import WeatherEntity
from homeassistant.const import TEMP_CELSIUS

from homeassistant.components.weather import (
    ATTR_CONDITION_CLEAR_NIGHT,
    ATTR_CONDITION_CLOUDY,
    ATTR_CONDITION_FOG,
    ATTR_CONDITION_HAIL,
    ATTR_CONDITION_LIGHTNING,
    ATTR_CONDITION_PARTLYCLOUDY,
    ATTR_CONDITION_POURING,
    ATTR_CONDITION_RAINY,
    ATTR_CONDITION_SNOWY,
    ATTR_CONDITION_SUNNY,

    ATTR_FORECAST_CONDITION,
    ATTR_FORECAST_PRECIPITATION_PROBABILITY,
    ATTR_FORECAST_TEMP,
    ATTR_FORECAST_TEMP_LOW,
    ATTR_FORECAST_TIME,
    ATTR_FORECAST_WIND_BEARING,
    ATTR_FORECAST_WIND_SPEED,

    DOMAIN as SENSOR_DOMAIN,
    Forecast,
    WeatherEntityFeature,
)

from .const import (
    CONDITION,
    DOMAIN,
    LOCATION,
    NOW_HUMI,
    NOW_TEMP,
    WIND_DIR,
    WIND_SPEED,
)
from .nweather_device import NWeatherDevice

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=10)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add a entity from a config_entry."""

    api = hass.data[DOMAIN]["api"][config_entry.entry_id]

    def async_add_entity():
        """Add sensor from sensor."""
        entities = []
        device = ["Naver Weather", "네이버날씨", "", ""]
        entities.append(NWeatherMain(device, api))

        if entities:
            async_add_entities(entities)

    async_add_entity()


class NWeatherMain(NWeatherDevice, WeatherEntity):
    """Representation of a weather condition."""
    _attr_native_temperature_unit = TEMP_CELSIUS
    
    @property
    def name(self) -> str:
        """Return the name of the device."""
        if not self.api.get_data(self.unique_id):
            self.api.set_data(self.unique_id, True)
            return self.device[0] + " " + str(self.api.count)
        elif self.area != "날씨":
            return self.area.split(" 날씨")[0]
        else:
            return self.device[1]

    @property
    def native_temperature(self):
        """Return the temperature."""
        try:
            return float(self.api.result.get(NOW_TEMP[0]))
        except Exception:
            return

    @property
    def humidity(self):
        """Return the humidity."""
        try:
            return int(self.api.result.get(NOW_HUMI[0]))
        except Exception:
            return

    @property
    def native_wind_speed(self):
        """Return the wind speed."""
        try:
            return float(self.api.result.get(WIND_SPEED[0])) * 3.6
        except Exception:
            return

    @property
    def wind_bearing(self):
        """Return the wind bearing."""
        return self.api.result.get(WIND_DIR[0])

    @property
    def condition(self):
        """Return the weather condition."""
        return self.api.result.get(CONDITION[0])

    @property
    def state(self):
        """Return the weather state."""
        return self.api.result.get(CONDITION[0])

    @property
    def attribution(self):
        """Return the attribution."""
        return f"{self.api.result.get(LOCATION[0])} - Weather forecast from Naver, Powered by miumida"

    @property
    def forecast(self) -> list[Forecast] | None:
        """Return the forecast."""
        #return self.api.forecast
        return self._forecast()

    async def async_forecast_daily(self) -> list[Forecast] | None:
        """Return the daily forecast in native units.
        
        Only implement this method if `WeatherEntityFeature.FORECAST_DAILY` is set
        """
        return self._forecast()

    @property
    def should_poll(self) -> bool:
        """No polling needed for this device."""
        return True

    async def async_update(self):
        """Update current conditions."""
        await self.api.update()

    def _forecast(self) -> list[Forecast] | None:
        forecast = []

        for data in self.api.forecast:
            next_day = {
                ATTR_FORECAST_TIME: data["datetime"],
                ATTR_FORECAST_CONDITION: data["condition"],
                ATTR_FORECAST_TEMP_LOW: data["templow"],
                ATTR_FORECAST_TEMP: data["temperature"],
                ATTR_FORECAST_PRECIPITATION_PROBABILITY: data["rain_rate_am"],
                #ATTR_FORECAST_WIND_BEARING: data[""],
                #ATTR_FORECAST_WIND_SPEED: data[""],
                
                # Not officially supported, but nice additions.
                "condition_am": data["condition_am"],
                "condition_pm": data["condition_pm"],

                "rain_rate_am": data["rain_rate_am"],
                "rain_rate_pm": data["rain_rate_pm"]
            }
            forecast.append(next_day)

        return forecast
