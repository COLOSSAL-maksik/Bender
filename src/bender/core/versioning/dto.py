from dataclasses import dataclass, field
from typing import Any

from bender.core.identity.models import Id, Namespace
from bender.core.provenance.models import Provenance
from bender.core.serialization.fingerprint import compute_fingerprint
from bender.core.serialization.json import ValidJsonType


@dataclass(frozen=True)
class VersionedArtifact:
    """
    The envelope for serialized Bender artifacts.
    Contains identity, provenance, versioning info, and the payload.
    """

    id: Id
    namespace: Namespace
    schema_name: str
    schema_version: int
    payload: ValidJsonType
    provenance: Provenance = field(default_factory=Provenance.empty)

    def fingerprint(self) -> str:
        """
        Computes the fingerprint of the meaningful contents.
        Excludes the instance ID, but includes namespace, schema, and payload.
        Provenance is intentionally excluded from the mathematical fingerprint,
        as identical outputs can come from different sources, but is retained in the envelope.
        """
        data = {
            "namespace": str(self.namespace),
            "schema_name": self.schema_name,
            "schema_version": self.schema_version,
            "payload": self.payload,
        }
        return compute_fingerprint(data)

    def serialize_envelope(self) -> dict[str, Any]:
        """Returns the dictionary representation of the envelope for JSON serialization."""
        return {
            "type": "bender_artifact",
            "id": str(self.id),
            "namespace": str(self.namespace),
            "schema_name": self.schema_name,
            "schema_version": self.schema_version,
            "payload": self.payload,
            "provenance": {
                "sources": [
                    {"id": str(s.id), "namespace": str(s.namespace)}
                    for s in self.provenance.sources
                ],
                "operation": {
                    "operation_id": str(self.provenance.operation.operation_id)
                    if self.provenance.operation and self.provenance.operation.operation_id
                    else None,
                    "version": self.provenance.operation.version
                    if self.provenance.operation
                    else None,
                }
                if self.provenance.operation
                else None,
            },
        }
