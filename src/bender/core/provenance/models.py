from collections.abc import Sequence
from dataclasses import dataclass

from bender.core.identity.models import Id, Namespace


@dataclass(frozen=True)
class ArtifactSource:
    """A reference to an artifact that contributed to this data."""

    id: Id
    namespace: Namespace


@dataclass(frozen=True)
class OperationRecord:
    """A record of the operation that produced this artifact."""

    operation_id: Id | None
    version: str | None


@dataclass(frozen=True)
class Provenance:
    """
    Immutable model of data provenance: what artifacts this artifact is derived from,
    and what operation created it.
    """

    sources: Sequence[ArtifactSource]
    operation: OperationRecord | None

    @classmethod
    def empty(cls) -> "Provenance":
        """Returns an empty Provenance record."""
        return cls(sources=(), operation=None)
