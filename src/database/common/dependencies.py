import uuid

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase


class BaseSQL(DeclarativeBase):
    __abstract__ = True

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
