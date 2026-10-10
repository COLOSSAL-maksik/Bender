import hashlib
from typing import Any

from .json import generate_canonical_json_bytes


def compute_fingerprint(obj: Any) -> str:
    """
    Computes a SHA-256 fingerprint for an object based on its canonical JSON representation.
    Only the provided object is used in the fingerprint. In standard Bender usage,
    this is called with the payload and explicitly included envelope fields, but not the ID.
    """
    canonical_bytes = generate_canonical_json_bytes(obj)
    return hashlib.sha256(canonical_bytes).hexdigest()
