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
