import json
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from geoalchemy2 import WKTElement
from shapely.geometry import shape

from src.api.schemas.field import FieldCreate, FieldUpdate
from src.common.exceptions import FieldNotFoundException
from src.models.field import Field
from src.utils import conversion


async def get_fields(
    db: AsyncSession,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    boundary: Optional[str] = None,
    filter_by: Optional[str] = None,
):
    queryset = select(Field).order_by(desc(Field.creation_date))

    if filter_by is None:
        queryset = queryset.where(Field.deletion_date == None)
    elif filter_by == "deleted":
        queryset = queryset.where(Field.deletion_date != None)

    if boundary is not None:
        # Convert the GeoJSON string into a Shapely geometry
        boundary_shape = shape(json.loads(boundary))

        # Convert Shapely shape to WKT and set SRID to 4326
        boundary_geom = func.ST_SetSRID(func.ST_GeomFromText(boundary_shape.wkt), 4326)

        # Use ST_Intersects to filter fields
        queryset = queryset.where(func.ST_Intersects(Field.boundary, boundary_geom))

    # Calculate total count after applying filters
    total_query = select(func.count()).select_from(queryset.subquery())
    total = await db.scalar(total_query)

    # Apply pagination if limit and offset are provided
    if limit is not None and offset is not None:
        queryset = queryset.limit(limit).offset(offset)

    result = await db.execute(queryset)
    fields = result.scalars().all()

    return fields, total


async def get_field(
    field_id: UUID, db: AsyncSession, include_deleted: bool = False
) -> Optional[Field]:
    query = select(Field).where(Field.id == field_id)
    if not include_deleted:
        query = query.where(Field.deletion_date == None)

    db_field = (await db.scalars(query)).first()
    if db_field is None:
        raise FieldNotFoundException(field_id=field_id)
    return db_field


async def get_field_by_boundary(boundary: dict, db: AsyncSession) -> Optional[Field]:
    # Convert GeoJSON boundary to WKT
    boundary_wkt = conversion.validate_and_convert_geojson(boundary)

    boundary_geom = func.ST_SetSRID(func.ST_GeomFromText(boundary_wkt), 4326)

    # Query the field that matches the given boundary
    result = await db.execute(
        select(Field).where(func.ST_Equals(Field.boundary, boundary_geom))
    )

    return result.scalar_one_or_none()


async def create_field(field: FieldCreate, db: AsyncSession) -> Field:
    # Validate and convert the boundary (GeoJSON) to WKTElement if provided
    if field.boundary:
        boundary_wkt = conversion.validate_and_convert_geojson(field.boundary)
        field_wkt = WKTElement(boundary_wkt, srid=4326)
    else:
        field_wkt = None

    # Prepare the field for the database
    db_field = Field(**field.model_dump())

    # Assign WKTElement to the db_field's boundary attribute before saving
    db_field.boundary = field_wkt  # type: ignore[assignment]

    db.add(db_field)
    await db.commit()
    await db.refresh(db_field)

    return db_field


async def update_field(field_id: UUID, field: FieldUpdate, db: AsyncSession) -> Field:
    db_field = await get_field(field_id=field_id, db=db, include_deleted=True)

    if field.boundary:
        boundary_wkt = conversion.validate_and_convert_geojson(field.boundary)
        setattr(db_field, "boundary", WKTElement(boundary_wkt, srid=4326))

    field_data = field.model_dump(exclude_unset=True)

    for key, value in field_data.items():
        if key != "boundary":  # Skip 'boundary' since it's already updated
            setattr(db_field, key, value)

    await db.commit()
    await db.refresh(db_field)

    return db_field


async def soft_delete_field(field_id: UUID, db: AsyncSession) -> Optional[Field]:
    db_field = await get_field(field_id=field_id, db=db)

    current_time = datetime.now()
    db_field.deletion_date = current_time  # type: ignore[assignment]
    await db.commit()

    return db_field
