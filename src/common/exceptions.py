from uuid import UUID


class FieldNotFoundException(Exception):
    def __init__(self, field_id: UUID):
        self.field_id = field_id
        super().__init__(f"Field with ID {field_id} does not exist")


class InvalidGeoJSONException(Exception):
    def __init__(self, message="Invalid GeoJSON format"):
        self.message = message
        super().__init__(self.message)


class SelfIntersectionException(Exception):
    def __init__(
        self, message="The provided geometry is self-intersecting and cannot be fixed"
    ):
        self.message = message
        super().__init__(self.message)
