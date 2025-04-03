from datetime import timedelta, datetime

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
    - If field exists and has an image, check if it is expired.
    - If expired or missing, fetch a new image, and update the field.
    - If no field exists, create one, fetch an image, and store it.
    """
    # Check if boundary exists in the database
    existing_field = await crud_field.get_field_by_boundary(
        boundary=satellite.boundary, db=db
    )

    current_time = datetime.now()

    if existing_field:
        # If field exists, has an image and not expired, return it
        if existing_field.image_url and existing_field.expiration_time > current_time:
            return existing_field

        # If field exists but has no image or expired, fetch from GEE and update it
        image_url = get_latest_sentinel_image(boundary=satellite.boundary)

        updated_field = await crud_field.update_field(
            field_id=existing_field.id,  # type: ignore[arg-type]
            field=FieldUpdate(
                image_url=image_url,
                expiration_time=current_time + timedelta(minutes=50),
            ),
            db=db,
        )

        return updated_field

    # If no field found, fetch image and create it
    image_url = get_latest_sentinel_image(boundary=satellite.boundary)

    new_field = await crud_field.create_field(
        FieldCreate(
            boundary=satellite.boundary,
            image_url=image_url,
            expiration_time=current_time + timedelta(minutes=50),
        ),
        db=db,
    )

    return new_field
