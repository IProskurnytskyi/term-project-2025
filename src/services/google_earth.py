import ee

from src.config.base import settings

ee.Initialize(project=settings.gee_project)


def get_latest_sentinel_image(boundary: dict):
    # Define the geometry
    ee_geometry = ee.Geometry.Polygon(boundary["coordinates"])

    # Use the updated dataset
    collection = ee.ImageCollection("COPERNICUS/S2_HARMONIZED").filterBounds(
        ee_geometry
    )

    # Get the newest image
    newest_image = collection.sort("system:time_start", False).first()

    # Select RGB bands (B4 = Red, B3 = Green, B2 = Blue)
    rgb_image = newest_image.select(["B4", "B3", "B2"]).reproject(
        crs="EPSG:4326", scale=30
    )

    # Apply visualization stretch (set min and max values for display)
    vis_params = {"min": 0, "max": 3000, "bands": ["B4", "B3", "B2"]}

    # Get thumbnail URL
    url = rgb_image.getThumbURL(
        {"region": ee_geometry, "scale": 30, "crs": "EPSG:4326", **vis_params}
    )

    return url
