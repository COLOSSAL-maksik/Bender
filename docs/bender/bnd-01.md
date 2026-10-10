# BND-01: Identity, Versioning & Serialization Foundation

This document defines the core data foundation for Bender artifacts.

## Core Concepts

### 1. Identity
Every artifact in Bender is assigned an immutable `Id` (a normalized UUIDv4). The ID represents the *concept* or *instance* of the object, completely independently of its content, file path, or relationships. If an object is modified and saved, its ID remains the same. A `Namespace` provides a domain grouping (e.g., `beam-planar`, `core-task`).

### 2. Provenance
To understand where data came from without relying on external databases, Bender artifacts carry a `Provenance` record. This explicitly lists the `ArtifactSource`s (other IDs and namespaces) that contributed to this data, and the `OperationRecord` that generated it.

### 3. Serialization Envelope
All data saved or exported from Bender is wrapped in a `VersionedArtifact` envelope.

```json
{
  "type": "bender_artifact",
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "namespace": "beam-planar",
  "schema_name": "problem_definition",
  "schema_version": 2,
  "payload": {
     // ... domain-specific data ...
  },
  "provenance": {
    "sources": [],
    "operation": null
  }
}
```

### 4. Canonical Serialization and Fingerprinting
Bender guarantees reproducible JSON serialization for verification purposes:
- UTF-8 encoding.
- Keys are strictly sorted.
- No whitespace around separators.
- `NaN` and `Infinity` are rejected.
- Duplicate keys are rejected upon loading.

The `fingerprint` is a SHA-256 hash computed over the **canonical JSON bytes** of an object containing `namespace`, `schema_name`, `schema_version`, and `payload`.
**Crucially, the `Id` and `Provenance` are excluded from the fingerprint.** This means two identical beams generated at different times by different processes will have different IDs and provenance, but the exact same fingerprint.

### 5. Schema Migrations
Bender does not use Alembic or database migrations for its internal artifact representations. Instead, it uses a functional `SchemaMigrationRegistry`.

When a `VersionedArtifact` is loaded:
1. We check the `schema_name`.
2. If `schema_version` is older than the current target version, we sequentially apply pure migration functions (e.g., `v1_to_v2`, `v2_to_v3`) to the `payload`.
3. The result is a new `VersionedArtifact` with the updated payload and the target schema version, while keeping the original `Id` and `Provenance` intact.
4. If a schema is unknown, a future version is encountered, or a migration step is missing, a structured error (e.g., `UnsupportedVersionError`, `MigrationError`) is raised.
