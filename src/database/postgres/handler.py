import logging

from sqlalchemy.engine.url import URL

from src.database.postgres.core import PostgreSQLCore

logger = logging.getLogger(__name__)


class PostgreSQLHandler(PostgreSQLCore):
    """
    A subclass of PostgreSQLHandler to handle database queries.
    """

    def __init__(self, db_url: URL = None, database: str = None) -> None:
        """
        Initializes the PostgreSQLCore with a database URL and connects to it.

        Args:
            db_url (str, optional): The database URL. Defaults to None.
            database (str, optional): The name of the database to connect to. Defaults to None.
        """
        super().__init__(db_url, database)
