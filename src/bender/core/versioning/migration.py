from collections.abc import Callable

from bender.core.diagnostics.errors import (
    MigrationError,
    UnknownSchemaError,
    UnsupportedVersionError,
)
from bender.core.versioning.dto import VersionedArtifact

# A migration function takes a payload and returns the new payload
MigrationFunction = Callable[
    [dict | list | str | int | float | bool | None], dict | list | str | int | float | bool | None
]


class SchemaMigrationRegistry:
    """
    Registry for schema migrations.
    Provides explicit paths to upgrade older DTO payloads to the current version.
    """

    def __init__(self):
        # Format: {schema_name: {from_version: migration_function}}
        self._migrations: dict[str, dict[int, MigrationFunction]] = {}
        # Format: {schema_name: current_version}
        self._current_versions: dict[str, int] = {}

    def register_schema(self, schema_name: str, current_version: int):
        """Registers a known schema and its current (max supported) version."""
        self._current_versions[schema_name] = current_version
        if schema_name not in self._migrations:
            self._migrations[schema_name] = {}

    def register_migration(self, schema_name: str, from_version: int, func: MigrationFunction):
        """Registers a transition from `from_version` to `from_version + 1`."""
        if schema_name not in self._migrations:
            self._migrations[schema_name] = {}
        self._migrations[schema_name][from_version] = func

    def migrate(self, artifact: VersionedArtifact) -> VersionedArtifact:
        """
        Migrates the artifact to the current registered version for its schema.
        Raises specific errors if the schema is unknown, the version is from the future,
        or a transition is missing.
        """
        if artifact.schema_name not in self._current_versions:
            raise UnknownSchemaError(artifact.schema_name)

        target_version = self._current_versions[artifact.schema_name]

        if artifact.schema_version > target_version:
            raise UnsupportedVersionError(
                artifact.schema_name, artifact.schema_version, target_version
            )

        if artifact.schema_version == target_version:
            return artifact  # Already at target version

        current_payload = artifact.payload
        current_version = artifact.schema_version

        # Apply migrations sequentially
        while current_version < target_version:
            if current_version not in self._migrations[artifact.schema_name]:
                raise MigrationError(
                    "Missing transition function.",
                    artifact.schema_name,
                    current_version,
                    current_version + 1,
                )

            try:
                migration_func = self._migrations[artifact.schema_name][current_version]
                # Note: deep copy is not strictly necessary here because we expect migrations to return new dicts,
                # but to be safe and enforce immutability of the old artifact, we don't mutate the old one.
                current_payload = migration_func(current_payload)
            except Exception as e:
                raise MigrationError(
                    f"Migration logic failed: {e}",
                    artifact.schema_name,
                    current_version,
                    current_version + 1,
                )
            current_version += 1

        return VersionedArtifact(
            id=artifact.id,
            namespace=artifact.namespace,
            schema_name=artifact.schema_name,
            schema_version=target_version,
            payload=current_payload,
            provenance=artifact.provenance,
        )
