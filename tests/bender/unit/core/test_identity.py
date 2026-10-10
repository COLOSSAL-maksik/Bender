import pytest

from bender.core.diagnostics.errors import InvalidIdError
from bender.core.identity.models import Id, Namespace


def test_valid_namespaces():
    ns1 = Namespace("beam-planar")
    assert ns1.value == "beam-planar"
    assert str(ns1) == "beam-planar"

    ns2 = Namespace("a" * 64)
    assert len(ns2.value) == 64


def test_invalid_namespaces():
    with pytest.raises(InvalidIdError, match="Invalid namespace format"):
        Namespace("Invalid-Caps")

    with pytest.raises(InvalidIdError, match="Invalid namespace format"):
        Namespace("spaces are bad")

    with pytest.raises(InvalidIdError, match="cannot start or end with a hyphen"):
        Namespace("-start")

    with pytest.raises(InvalidIdError, match="cannot start or end with a hyphen"):
        Namespace("end-")

    with pytest.raises(InvalidIdError, match="Invalid namespace format"):
        Namespace("")  # Empty string

    with pytest.raises(InvalidIdError, match="Invalid namespace format"):
        Namespace("a" * 65)  # Too long


def test_valid_ids():
    id1 = Id.generate()
    assert isinstance(id1.value, str)
    assert len(id1.value) == 36
    assert str(id1) == id1.value

    # Test normalization
    upper_uuid = "550E8400-E29B-41D4-A716-446655440000"
    id2 = Id(upper_uuid)
    assert id2.value == upper_uuid.lower()


def test_invalid_ids():
    with pytest.raises(InvalidIdError, match="Invalid ID format"):
        Id("not-a-uuid")

    with pytest.raises(InvalidIdError, match="Invalid ID format"):
        Id("12345678-1234-1234-1234-12345678901")  # Too short
