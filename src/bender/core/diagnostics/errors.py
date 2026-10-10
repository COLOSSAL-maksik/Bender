class BenderError(Exception):
    """Base exception for all Bender-specific errors."""



class InvalidIdError(BenderError):
    """Raised when an ID or Namespace format is invalid."""

    def __init__(self, message: str, invalid_value: str | None = None, field: str | None = None):
        super().__init__(message)
        self.invalid_value = invalid_value
        self.field = field


class SerializationError(BenderError):
    """Raised when canonical serialization fails (e.g., unsupported types, invalid floats)."""

    def __init__(self, message: str, field: str | None = None):
        super().__init__(message)
        self.field = field


class DeserializationError(BenderError):
    """Raised when JSON parsing fails (e.g., syntax errors, duplicate keys)."""



class UnknownSchemaError(BenderError):
    """Raised when trying to load an artifact with an unregistered schema name."""

    def __init__(self, schema_name: str):
        super().__init__(f"Unknown schema: {schema_name}")
        self.schema_name = schema_name


class UnsupportedVersionError(BenderError):
    """Raised when trying to load an artifact with a version that cannot be handled."""

    def __init__(self, schema_name: str, version: int, max_supported: int):
        super().__init__(
            f"Unsupported version {version} for schema {schema_name}. Max supported is {max_supported}.",
        )
        self.schema_name = schema_name
        self.version = version
        self.max_supported = max_supported


class MigrationError(BenderError):
    """Raised when a schema migration fails or is not possible."""

    def __init__(self, message: str, schema_name: str, from_version: int, to_version: int):
        super().__init__(
            f"Migration error ({schema_name} v{from_version} -> v{to_version}): {message}",
        )
        self.schema_name = schema_name
        self.from_version = from_version
        self.to_version = to_version
