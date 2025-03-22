from typing import Optional, Any, Dict

from pydantic import BaseModel, field_validator

from src.utils.validation import validate_geojson


class SatelliteCreate(BaseModel):
    boundary: dict

    @field_validator("boundary", mode="before")
    @classmethod
    def validate_boundary(cls, value: Any) -> Optional[Dict[str, Any]]:
        return validate_geojson(value, "Boundary")
