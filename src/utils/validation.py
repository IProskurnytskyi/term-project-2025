from typing import Optional, Any, Dict

from geoalchemy2 import WKBElement

from src.utils.conversion import convert_wkb_to_geojson


def validate_geojson(value: Any, field_name: str) -> Optional[Dict[str, Any]]:
    """
    Validate GeoJSON-like input. Allows None values but raises errors for invalid GeoJSON if present.
    """
    if value is None:
        return None

    # Convert WKBElement to GeoJSON if the value is of type WKBElement
    if isinstance(value, WKBElement):
        return convert_wkb_to_geojson(value)  # type: ignore[no-any-return]

    # Validate if the value is in correct GeoJSON format
    if not isinstance(value, dict):
        raise ValueError(
            f"{field_name} must be a dictionary representing a GeoJSON object"
        )

    # Validate the GeoJSON object type
    geojson_type = value.get("type")
    if geojson_type not in {"Polygon"}:
        raise ValueError(
            f"{field_name} must be a valid GeoJSON type (e.g., Polygon), "
            f"but got '{geojson_type}'"
        )

    coordinates = value.get("coordinates")
    if not coordinates or not isinstance(coordinates, list):
        raise ValueError(
            f"{field_name} must include valid 'coordinates' as a list of points"
        )

    return value
