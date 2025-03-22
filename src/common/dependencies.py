from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.postgres.handler import PostgreSQLHandler as DatabaseHandler


async def get_database_dependency() -> DatabaseHandler:
    """
    Provides a database handler dependency for use in FastAPI routes or other dependency-injection contexts.

    Returns:
        DatabaseHandler: An instance of `DatabaseHandler` for interacting with the database.
    """
    return DatabaseHandler()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Get an asynchronous database session.

    This function creates and returns an asynchronous database session using the provided
    DatabaseHandler. The session is yielded to the caller, allowing them to use it.

    Returns:
        AsyncSession: An asynchronous database session.

    Raises:
        Any exceptions raised by the DatabaseHandler's session_factory method.
    """
    db_handler = DatabaseHandler()

    async_session = db_handler.session_factory()

    try:
        yield async_session
    finally:
        await async_session.close()
