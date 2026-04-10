from pydantic import BaseModel


class CurrentWeather(BaseModel):
    temperature: float
    apparent_temperature: float
    humidity: int
    precipitation: float
    wind_speed: float
    wind_direction: int
    weather_code: int
    weather_description: str


class DailyForecast(BaseModel):
    date: str
    temperature_max: float
    temperature_min: float
    precipitation_sum: float
    wind_speed_max: float
    weather_code: int
    weather_description: str


class WeatherResponse(BaseModel):
    latitude: float
    longitude: float
    timezone: str
    current: CurrentWeather
    daily: list[DailyForecast]
