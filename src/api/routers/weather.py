from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from geoalchemy2.shape import to_shape
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas.weather import WeatherResponse, CurrentWeather, DailyForecast
from src.common.dependencies import get_db
from src.common.exceptions import FieldNotFoundException
from src.database.postgres.crud import field as crud_field
from src.services.weather import get_weather_for_coordinates, describe_weather_code

router = APIRouter(prefix="/fields", tags=["weather"])


@router.get("/{field_id}/weather", response_model=WeatherResponse)
async def get_field_weather(
    field_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Get current weather and 7-day forecast for a field's location.
    Computes the centroid of the field boundary and fetches weather data from Open-Meteo.
    """
    try:
        field = await crud_field.get_field(field_id=field_id, db=db)
    except FieldNotFoundException as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    centroid = to_shape(field.boundary).centroid
    latitude = centroid.y
    longitude = centroid.x

    try:
        raw = get_weather_for_coordinates(latitude, longitude)
    except Exception as exc:
        raise HTTPException(
            status_code=502, detail=f"Weather service error: {exc}"
        ) from exc

    current_data = raw["current"]
    current = CurrentWeather(
        temperature=current_data["temperature_2m"],
        apparent_temperature=current_data["apparent_temperature"],
        humidity=current_data["relative_humidity_2m"],
        precipitation=current_data["precipitation"],
        wind_speed=current_data["wind_speed_10m"],
        wind_direction=current_data["wind_direction_10m"],
        weather_code=current_data["weather_code"],
        weather_description=describe_weather_code(current_data["weather_code"]),
    )

    daily_data = raw["daily"]
    daily = [
        DailyForecast(
            date=daily_data["time"][idx],
            temperature_max=daily_data["temperature_2m_max"][idx],
            temperature_min=daily_data["temperature_2m_min"][idx],
            precipitation_sum=daily_data["precipitation_sum"][idx],
            wind_speed_max=daily_data["wind_speed_10m_max"][idx],
            weather_code=daily_data["weather_code"][idx],
            weather_description=describe_weather_code(daily_data["weather_code"][idx]),
        )
        for idx in range(len(daily_data["time"]))
    ]

    return WeatherResponse(
        latitude=latitude,
        longitude=longitude,
        timezone=raw.get("timezone", "UTC"),
        current=current,
        daily=daily,
    )
