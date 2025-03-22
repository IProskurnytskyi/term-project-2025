from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.google_earth import get_latest_sentinel_image
from src.api.schemas.satellite import SatelliteCreate
from src.api.schemas.field import FieldRead, FieldCreate, FieldUpdate
from src.common.dependencies import get_db
from src.database.postgres.crud import field as crud_field

router = APIRouter(prefix="/satellite-image", tags=["satellite"])


@router.post("/", response_model=FieldRead)
async def get_satellite_image(
    satellite: SatelliteCreate, db: AsyncSession = Depends(get_db)
):
    """
    Checks if a field with the given boundary exists in the database.
    - If it exists and has an image, return it.
    - If it exists but has no image, fetch the image, update the field, and return it.
    - If no field exists, create one, fetch the image, and return it.
    """
    # Check if boundary exists in the database
    existing_field = await crud_field.get_field_by_boundary(
        boundary=satellite.boundary, db=db
    )

    if existing_field:
        # If field exists and has an image, return it
        if existing_field.image_url:
            return existing_field

        # If field exists but has no image, fetch from GEE and update it
        image_url = get_latest_sentinel_image(boundary=satellite.boundary)

        updated_field = await crud_field.update_field(
            field_id=existing_field.id,  # type: ignore[arg-type]
            field=FieldUpdate(image_url=image_url),
            db=db,
        )

        return updated_field

    # If no field found, create it and fetch image
    image_url = get_latest_sentinel_image(boundary=satellite.boundary)

    new_field = await crud_field.create_field(
        FieldCreate(boundary=satellite.boundary, image_url=image_url), db=db
    )

    return new_field
