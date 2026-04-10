from datetime import date
from typing import Any, Dict, Optional

from pydantic import BaseModel, field_validator

from src.utils.validation import validate_geojson


class NdviComparisonRequest(BaseModel):
    boundary: dict
    date_before_start: date
    date_before_end: date
    date_after_start: date
    date_after_end: date

    @field_validator("boundary", mode="before")
    @classmethod
    def validate_boundary(cls, value: Any) -> Optional[Dict[str, Any]]:
        return validate_geojson(value, "Boundary")


class NdviComparisonResponse(BaseModel):
    ndvi_before_url: str
    ndvi_after_url: str
    ndvi_diff_url: str
