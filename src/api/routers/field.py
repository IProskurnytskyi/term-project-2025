from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Params
from fastapi_pagination.links import Page
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas.field import FieldRead, FieldCreate
from src.common.dependencies import get_db
from src.common.exceptions import (
    FieldNotFoundException,
    InvalidGeoJSONException,
    SelfIntersectionException,
)
from src.database.postgres.crud import field as crud_field
from src.api.common.decorators import validate_filter_by

router = APIRouter(prefix="/fields", tags=["fields"])


@router.get("/", response_model=Page[FieldRead])
@validate_filter_by
async def list_fields(
    db: AsyncSession = Depends(get_db),
    boundary: Optional[str] = None,
    filter_by: Optional[str] = None,
    params: Params = Depends(),
):
    """
    Retrieve a paginated list of fields.

    ### Arguments
    - **boundary** (`Optional[str]`): Filter fields by GeoJSON boundary. Defaults to `None`.
    - **filter_by** (`Optional[str]`): Specifies how to filter fields. Defaults to `None`,
        which retrieves only active fields. Possible values: `deleted`, or `all`.

    ### Returns
    - **Page[FieldRead]**: A paginated list of fields.

    ### Raises
    - **HTTPException**:
        - **500**: If an unexpected error occurs during the database query.
    """
    fields, total = await crud_field.get_fields(
        db=db,
        limit=params.size,
        offset=(params.page - 1) * params.size,
        boundary=boundary,
        filter_by=filter_by,
    )

    return Page.create(items=fields, params=params, total=total)


@router.get("/{field_id}", response_model=FieldRead)
async def get_field(
    field_id: UUID,
    db: AsyncSession = Depends(get_db),
    include_deleted: bool = False,
):
    """
    Retrieve a specific field by ID.

    ### Arguments
    - **field_id** (`UUID`): The UUID of the field to retrieve.
    - **include_deleted** (`bool`): Whether to include soft-deleted fields in the result. Defaults to `False`.

    ### Returns
    - **FieldRead**: The field data.

    ### Raises
    - **HTTPException**:
        - If the field is not found (404).
    """
    try:
        return await crud_field.get_field(
            field_id=field_id, db=db, include_deleted=include_deleted
        )
    except FieldNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.post("/", response_model=FieldRead)
async def create_field(field: FieldCreate, db: AsyncSession = Depends(get_db)):
    """
    Create a new field.

    ### Arguments
    - **field** (`FieldCreate`): The data to create a new field.

    ### Returns
    - **FieldRead**: The created field data.

    ### Raises
    - **HTTPException**:
        - If the provided values are invalid (400).
        - If the GeoJSON is invalid (400).
        - If the geometry is self-intersecting and cannot be fixed (400).
    """
    try:
        return await crud_field.create_field(field=field, db=db)
    except (InvalidGeoJSONException, SelfIntersectionException) as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.delete("/{field_id}")
async def delete_field(field_id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Soft deletes a field. Soft deletion marks the field as deleted by setting a deletion date,
    but it remains stored in the database. Soft-deleted fields are excluded from regular queries, but you can
    view them by using the 'deleted' or 'all' filter on 'filter_by' parameter when retrieving fields.

    ### Arguments
    - **field_id** (`UUID`): The UUID of the field to delete.

    ### Returns
    - **dict**: A message indicating successful deletion.

    ### Raises
    - **HTTPException**:
        - If the field is not found (404).
    """
    try:
        await crud_field.soft_delete_field(field_id=field_id, db=db)
        return {"message": "Field has been deleted successfully"}
    except FieldNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
