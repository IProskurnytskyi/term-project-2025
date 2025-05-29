import logging

from typing import Optional

from sqlalchemy import text
from sqlalchemy.engine.url import URL
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.database.common.dependencies import BaseSQL
from src.config.base import settings

logger = logging.getLogger(__name__)


class PostgreSQLCore:
    """
    A class to handle core PostgreSQL operations using SQLAlchemy.

    Attributes:
        db_url (str): The database URL.
        engine: The SQLAlchemy engine.
        session_factory: A SQLAlchemy session factory.
    """

    def __init__(
        self, db_url: Optional[URL] = None, database: Optional[str] = None
    ) -> None:
        """
        Initializes the PostgreSQLCore with a database URL and connects to it.

        Args:
            db_url (str, optional): The database URL. Defaults to None.
            database (str, optional): The name of the database to connect to. Defaults to None.
        """
        self.db_url = (
            db_url
            if db_url
            else self.build_db_url(database or settings.postgres_database)
        )
        self.base_model = BaseSQL
        self.engine = create_async_engine(self.db_url)
        self.session_factory = async_sessionmaker(
            bind=self.engine, expire_on_commit=False, class_=AsyncSession
        )

    @staticmethod
    def build_db_url(database: str) -> URL:
        """
        Builds the database URL using the provided database name and settings.

        Args:
            database (str): The name of the database.

        Returns:
            str: The constructed database URL.
        """
        if settings.cloud_sql_connection:
            return URL.create(
                drivername="postgresql+asyncpg",
                username=settings.postgres_username,
                password=settings.postgres_password,
                database=database,
                query={
                    "host": f"/cloudsql/{settings.cloud_sql_connection}/.s.PGSQL.5432"
                },
            )

        return URL.create(
            drivername="postgresql+asyncpg",
            username=settings.postgres_username,
            password=settings.postgres_password,
            host=settings.postgres_host,
            port=int(settings.postgres_port),
            database=database,
        )

    async def health_check(self) -> bool:
        """
        Performs a health check on the database.

        Returns:
            bool: True if the database is accessible and operational, False otherwise.
        """
        try:
            async with self.engine.connect() as connection:
                result = await connection.execute(text("SELECT 1"))
                return bool(result.scalar())
        except SQLAlchemyError as e:
            logger.error("Database health check failed: %s", e)
            return False
