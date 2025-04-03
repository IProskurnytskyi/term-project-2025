from datetime import datetime
from typing import Optional, Any, Dict
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, ConfigDict

from src.utils.validation import validate_geojson


class FieldBase(BaseModel):
    boundary: dict
    image_url: Optional[str] = Field(default=None, examples=[None])

    @field_validator("boundary", mode="before")
    @classmethod
    def validate_boundary(cls, value: Any) -> Optional[Dict[str, Any]]:
        return validate_geojson(value, "Boundary")


class FieldCreate(FieldBase):
    expiration_time: Optional[datetime] = Field(default=None, examples=[None])


class FieldUpdate(FieldBase):
    boundary: Optional[dict] = Field(default=None, examples=[{}])
    expiration_time: Optional[datetime] = Field(default=None, examples=[None])


class FieldRead(FieldBase):
    id: UUID
    creation_date: datetime
    deletion_date: Optional[datetime] = Field(default=None, examples=[None])

    model_config = ConfigDict(from_attributes=True)
