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
