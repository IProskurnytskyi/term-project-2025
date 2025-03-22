from shapely.geometry import shape, mapping
from shapely.validation import explain_validity
from geoalchemy2.shape import to_shape

from src.common.exceptions import InvalidGeoJSONException, SelfIntersectionException


def validate_and_convert_geojson(geojson_data: dict):
    """
    Validates the GeoJSON, converts it to WKT format, and fixes self-intersections if necessary.
    Raises exceptions if validation fails or the geometry cannot be fixed.
    """
    try:
        # Convert GeoJSON to a Shapely shape
        geom = shape(geojson_data)
    except (ValueError, TypeError) as exc:
        raise InvalidGeoJSONException() from exc

    # Check validity of the geometry
    if not geom.is_valid:
        if "Self-intersection" in explain_validity(geom):
            # Attempt to fix self-intersecting geometry
            geom = geom.buffer(0)
            if not geom.is_valid:
                raise SelfIntersectionException()
        else:
            raise InvalidGeoJSONException(message=explain_validity(geom))

    # Return the WKT representation
    return geom.wkt


def convert_wkb_to_geojson(wkb_element):
    """
    Convert a WKB (Well-Known Binary) element to a GeoJSON-like dictionary.

    This function takes a WKB element, which represents geometric data in binary format,
    and converts it to a GeoJSON-like dictionary that describes the geometry. The conversion
    is performed using Shapely's `to_shape` function to create a Shapely geometry object,
    and then the `mapping` function is used to produce the GeoJSON representation.
    """
    if wkb_element is None:
        return None
    shape_obj = to_shape(wkb_element)
    return mapping(shape_obj)  # Convert Shapely shape to GeoJSON-like dict
