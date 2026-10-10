import pytest

from bender.core.diagnostics.errors import (
    MigrationError,
    UnknownSchemaError,
    UnsupportedVersionError,
)
from bender.core.identity.models import Id, Namespace
from bender.core.versioning.dto import VersionedArtifact
from bender.core.versioning.migration import SchemaMigrationRegistry


def test_versioned_artifact_fingerprint_excludes_id_and_provenance():
    id1 = Id.generate()
    id2 = Id.generate()
    ns = Namespace("test-ns")
    payload = {"data": 123}

    art1 = VersionedArtifact(
        id=id1, namespace=ns, schema_name="test_schema", schema_version=1, payload=payload,
    )
    art2 = VersionedArtifact(
        id=id2, namespace=ns, schema_name="test_schema", schema_version=1, payload=payload,
    )

    assert art1.id != art2.id
    assert art1.fingerprint() == art2.fingerprint()


def test_migration_registry_successful_migration():
    registry = SchemaMigrationRegistry()
    registry.register_schema("test_schema", 3)

    def migrate_1_to_2(payload):
        # Rename 'old_field' to 'new_field'
        return {"new_field": payload.get("old_field", "")}

    def migrate_2_to_3(payload):
        # Add 'extra_field'
        new_payload = dict(payload)
        new_payload["extra_field"] = True
        return new_payload

    registry.register_migration("test_schema", 1, migrate_1_to_2)
    registry.register_migration("test_schema", 2, migrate_2_to_3)

    art_v1 = VersionedArtifact(
        id=Id.generate(),
        namespace=Namespace("test-ns"),
        schema_name="test_schema",
        schema_version=1,
        payload={"old_field": "value"},
    )

    migrated_art = registry.migrate(art_v1)

    assert migrated_art.schema_version == 3
    assert migrated_art.payload == {"new_field": "value", "extra_field": True}
    assert migrated_art.id == art_v1.id  # ID preserved
    assert migrated_art.provenance == art_v1.provenance  # Provenance preserved

    # Original artifact unchanged
    assert art_v1.payload == {"old_field": "value"}
    assert art_v1.schema_version == 1


def test_migration_registry_already_at_target():
    registry = SchemaMigrationRegistry()
    registry.register_schema("test_schema", 2)

    art = VersionedArtifact(
        id=Id.generate(),
        namespace=Namespace("test-ns"),
        schema_name="test_schema",
        schema_version=2,
        payload={"data": 1},
    )

    migrated_art = registry.migrate(art)
    assert migrated_art is art


def test_migration_registry_unknown_schema():
    registry = SchemaMigrationRegistry()
    art = VersionedArtifact(
        id=Id.generate(),
        namespace=Namespace("test-ns"),
        schema_name="unknown",
        schema_version=1,
        payload={},
    )

    with pytest.raises(UnknownSchemaError):
        registry.migrate(art)


def test_migration_registry_unsupported_future_version():
    registry = SchemaMigrationRegistry()
    registry.register_schema("test_schema", 1)

    art = VersionedArtifact(
        id=Id.generate(),
        namespace=Namespace("test-ns"),
        schema_name="test_schema",
        schema_version=2,
        payload={},
    )

    with pytest.raises(UnsupportedVersionError):
        registry.migrate(art)


def test_migration_registry_missing_transition():
    registry = SchemaMigrationRegistry()
    registry.register_schema("test_schema", 3)

    def migrate_1_to_2(payload):
        return payload

    registry.register_migration("test_schema", 1, migrate_1_to_2)
    # Missing 2 -> 3

    art = VersionedArtifact(
        id=Id.generate(),
        namespace=Namespace("test-ns"),
        schema_name="test_schema",
        schema_version=1,
        payload={},
    )

    with pytest.raises(MigrationError, match="Missing transition function"):
        registry.migrate(art)


def test_migration_registry_migration_logic_failure():
    registry = SchemaMigrationRegistry()
    registry.register_schema("test_schema", 2)

    def failing_migration(payload):
        raise ValueError("Something went wrong")

    registry.register_migration("test_schema", 1, failing_migration)

    art = VersionedArtifact(
        id=Id.generate(),
        namespace=Namespace("test-ns"),
        schema_name="test_schema",
        schema_version=1,
        payload={},
    )

    with pytest.raises(MigrationError, match="Migration logic failed: Something went wrong"):
        registry.migrate(art)
