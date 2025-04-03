from sqlalchemy import Column, String, DateTime, func
from geoalchemy2 import Geometry

from src.database.common.dependencies import BaseSQL


class Field(BaseSQL):
    __tablename__ = "fields"

    boundary = Column(Geometry(geometry_type="POLYGON", srid=4326), nullable=False)
    image_url = Column(String, nullable=True)
    expiration_time = Column(DateTime, nullable=False, server_default=func.now())
    creation_date = Column(DateTime, nullable=False, server_default=func.now())
    deletion_date = Column(DateTime, nullable=True, default=None)
