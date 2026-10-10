import re
import uuid
from dataclasses import dataclass
from typing import Self

from bender.core.diagnostics.errors import InvalidIdError

# Namespace regex: lowercase alphanumeric and hyphens. Length 1-64.
NAMESPACE_REGEX = re.compile(r"^[a-z0-9\-]{1,64}$")


@dataclass(frozen=True)
class Namespace:
    """An immutable namespace identifier for artifacts and mechanics domains."""

    value: str

    def __post_init__(self):
        if not NAMESPACE_REGEX.match(self.value):
            raise InvalidIdError(
                f"Invalid namespace format. Must match {NAMESPACE_REGEX.pattern}",
                invalid_value=self.value,
            )
        if self.value.startswith("-") or self.value.endswith("-"):
            raise InvalidIdError(
                "Namespace cannot start or end with a hyphen", invalid_value=self.value,
            )

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Id:
    """An immutable, opaque unique identifier for a Bender artifact.
    Backed by a UUIDv4 string to guarantee independence from contents and paths.
    """

    value: str

    def __post_init__(self):
        try:
            val = uuid.UUID(self.value, version=4)
            # Normalise to lower case standard format
            # This is a bit of a hack around frozen dataclass restrictions,
            # but object.__setattr__ works for initialization.
            if str(val) != self.value:
                object.__setattr__(self, "value", str(val))
        except ValueError:
            raise InvalidIdError(
                "Invalid ID format. Must be a valid UUIDv4 string.", invalid_value=self.value,
            )

    @classmethod
    def generate(cls) -> Self:
        """Generates a new random UUIDv4-based ID."""
        return cls(str(uuid.uuid4()))

    def __str__(self) -> str:
        return self.value
