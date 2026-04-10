from datetime import date

import ee

from src.config.base import settings

ee.Initialize(project=settings.gee_project)


def get_latest_sentinel_image(boundary: dict):
    # Define the geometry
    ee_geometry = ee.Geometry.Polygon(boundary["coordinates"])

    # Use the updated Sentinel-2 dataset, filter out cloudy images
    collection = (
        ee.ImageCollection("COPERNICUS/S2_HARMONIZED")
        .filterBounds(ee_geometry)
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20))
        .sort("system:time_start", False)
    )

    # Get the newest clear image
    newest_image = collection.first()

    # Select RGB bands (B4 = Red, B3 = Green, B2 = Blue)
    rgb_image = newest_image.select(["B4", "B3", "B2"])

    # Apply visualization parameters
    vis_params = {"min": 0, "max": 3000, "bands": ["B4", "B3", "B2"]}

    url = rgb_image.getThumbURL(
        {
            "region": ee_geometry,
            "scale": 10,
            **vis_params,
        }
    )

    return url


def get_ndvi_image(boundary: dict) -> str:
    ee_geometry = ee.Geometry.Polygon(boundary["coordinates"])

    collection = (
        ee.ImageCollection("COPERNICUS/S2_HARMONIZED")
        .filterBounds(ee_geometry)
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20))
        .sort("system:time_start", False)
    )

    newest_image = collection.first()

    # NDVI = (NIR - Red) / (NIR + Red), where NIR = B8, Red = B4
    ndvi = newest_image.normalizedDifference(["B8", "B4"]).rename("NDVI")

    # Color palette: red (dead/bare) -> yellow -> green (healthy vegetation)
    vis_params = {
        "min": -0.2,
        "max": 0.8,
        "palette": ["d73027", "fc8d59", "fee08b", "d9ef8b", "91cf60", "1a9850"],
    }

    url = ndvi.getThumbURL(
        {
            "region": ee_geometry,
            "scale": 10,
            **vis_params,
        }
    )

    return url


def get_sar_change_detection(
    boundary: dict,
    date_before_start: date,
    date_before_end: date,
    date_after_start: date,
    date_after_end: date,
) -> str:
    """
    Compute SAR change detection between two time periods using Sentinel-1 VV backscatter.
    Red = decrease in backscatter (potential destruction/change).
    Blue = increase in backscatter.
    """
    ee_geometry = ee.Geometry.Polygon(boundary["coordinates"])

    def get_sar_composite(start: date, end: date) -> ee.Image:
        return (
            ee.ImageCollection("COPERNICUS/S1_GRD")
            .filterBounds(ee_geometry)
            .filterDate(start.isoformat(), end.isoformat())
            .filter(ee.Filter.listContains("transmitterReceiverPolarisation", "VV"))
            .filter(ee.Filter.eq("instrumentMode", "IW"))
            .select("VV")
            .median()
        )

    before_composite = get_sar_composite(date_before_start, date_before_end)
    after_composite = get_sar_composite(date_after_start, date_after_end)

    # Positive = increase, negative = decrease in backscatter
    difference = after_composite.subtract(before_composite).rename("change")

    vis_params = {
        "min": -5,
        "max": 5,
        "palette": [
            "d73027",
            "f46d43",
            "fdae61",
            "ffffff",
            "abd9e9",
            "74add1",
            "4575b4",
        ],
    }

    url = difference.getThumbURL(
        {
            "region": ee_geometry,
            "scale": 10,
            **vis_params,
        }
    )

    return url
