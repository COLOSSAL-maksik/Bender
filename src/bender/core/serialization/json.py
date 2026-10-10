import json
import math
from typing import Any

from bender.core.diagnostics.errors import DeserializationError, SerializationError

# Valid types for our canonical JSON representation
# We strictly exclude custom classes to prevent execution vulnerabilities
ValidJsonType = dict[str, "ValidJsonType"] | list["ValidJsonType"] | str | int | float | bool | None


def _validate_for_canonical(obj: Any, path: str = "$") -> ValidJsonType:
    """Recursively checks if the object is valid for serialization and rejects NaN/Infinity."""
    if obj is None or isinstance(obj, bool) or isinstance(obj, int):
        return obj
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            raise SerializationError(
                "NaN and Infinity are not allowed in JSON serialization.", field=path,
            )
        return obj
    if isinstance(obj, str):
        return obj
    if isinstance(obj, list) or isinstance(obj, tuple):
        # We accept tuples here but they will be serialized as lists.
        # This keeps the output deterministic.
        return [_validate_for_canonical(item, f"{path}[{i}]") for i, item in enumerate(obj)]
    if isinstance(obj, dict):
        if not all(isinstance(k, str) for k in obj.keys()):
            raise SerializationError("All dictionary keys must be strings.", field=path)
        return {k: _validate_for_canonical(v, f"{path}.{k}") for k, v in obj.items()}
    raise SerializationError(
        f"Unsupported type for canonical serialization: {type(obj)}", field=path,
    )


def generate_canonical_json_bytes(obj: Any) -> bytes:
    """Generates deterministic UTF-8 encoded bytes for a JSON object.
    - Keys are sorted.
    - No spaces around separators.
    - NaN and Infinity are rejected.
    - Types are strictly checked.
    """
    validated = _validate_for_canonical(obj)
    # separators=(',', ':') removes whitespace
    # sort_keys=True ensures consistent dictionary order
    json_str = json.dumps(
        validated, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":"),
    )
    return json_str.encode("utf-8")


def object_pairs_hook_reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Hook for json.loads to reject duplicate keys in objects."""
    d = {}
    for k, v in pairs:
        if k in d:
            raise DeserializationError(f"Duplicate key found during JSON parsing: '{k}'")
        d[k] = v
    return d


def load_strict_json(json_bytes: bytes | str) -> ValidJsonType:
    """Loads JSON bytes strictly, rejecting duplicate keys and non-standard float values.
    """
    if isinstance(json_bytes, bytes):
        json_bytes = json_bytes.decode("utf-8")

    try:
        obj = json.loads(
            json_bytes,
            object_pairs_hook=object_pairs_hook_reject_duplicates,
            parse_constant=lambda c: _reject_nan_inf(c),
        )
        return obj
    except json.JSONDecodeError as e:
        raise DeserializationError(f"Failed to parse JSON: {e}")


def _reject_nan_inf(val: str) -> float:
    raise DeserializationError(f"NaN and Infinity are not allowed in JSON parsing: {val}")
