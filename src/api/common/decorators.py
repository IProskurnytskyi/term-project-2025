from functools import wraps
from typing import Optional

from fastapi import HTTPException


def validate_filter_by(func):
    """
    Decorator to validate the `filter_by` parameter for FastAPI endpoint functions.

    This decorator checks if the `filter_by` parameter is one of the allowed values:
    `None`, `"deleted"`, or `"all"`. If the parameter is invalid, it raises an HTTPException
    with a 400 status code.

    Args:
        func (Callable): The FastAPI endpoint function to wrap.

    Returns:
        Callable: The wrapped function with validation applied to the `filter_by` parameter.

    Raises:
        HTTPException: If the `filter_by` parameter is not one of the allowed values.
    """

    @wraps(func)
    async def wrapper(*args, filter_by: Optional[str] = None, **kwargs):
        if filter_by not in [None, "deleted", "all"]:
            raise HTTPException(
                status_code=400,
                detail="Incorrect value for filter_by parameter. Possible values: 'deleted', or 'all'",
            )
        return await func(*args, filter_by=filter_by, **kwargs)

    return wrapper
