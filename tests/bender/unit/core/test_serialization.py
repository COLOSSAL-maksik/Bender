import math
import os
import subprocess

import pytest

from bender.core.diagnostics.errors import DeserializationError, SerializationError
from bender.core.serialization.fingerprint import compute_fingerprint
from bender.core.serialization.json import generate_canonical_json_bytes, load_strict_json


def test_canonical_json_ordering():
    dict1 = {"b": 2, "a": 1, "c": 3}
    dict2 = {"a": 1, "c": 3, "b": 2}

    bytes1 = generate_canonical_json_bytes(dict1)
    bytes2 = generate_canonical_json_bytes(dict2)

    assert bytes1 == bytes2
    assert bytes1 == b'{"a":1,"b":2,"c":3}'


def test_canonical_json_rejects_nan_inf():
    with pytest.raises(SerializationError, match="NaN and Infinity are not allowed"):
        generate_canonical_json_bytes({"val": math.nan})

    with pytest.raises(SerializationError, match="NaN and Infinity are not allowed"):
        generate_canonical_json_bytes({"val": math.inf})


def test_canonical_json_rejects_invalid_types():
    class CustomObj:
        pass

    with pytest.raises(SerializationError, match="Unsupported type"):
        generate_canonical_json_bytes({"obj": CustomObj()})

    with pytest.raises(SerializationError, match="All dictionary keys must be strings"):
        generate_canonical_json_bytes({1: "one"})


def test_load_strict_json_rejects_duplicates():
    json_str = '{"a": 1, "a": 2}'
    with pytest.raises(DeserializationError, match="Duplicate key"):
        load_strict_json(json_str)


def test_load_strict_json_rejects_nan_inf():
    json_str = '{"val": NaN}'
    with pytest.raises(DeserializationError, match="NaN and Infinity are not allowed"):
        load_strict_json(json_str)


def test_load_strict_json_valid():
    json_str = '{"a": 1, "b": "test", "c": [1, 2, 3], "d": {"nested": true}}'
    obj = load_strict_json(json_str)
    assert obj["a"] == 1
    assert obj["b"] == "test"
    assert obj["c"] == [1, 2, 3]
    assert obj["d"]["nested"] is True


def test_fingerprint_changes_on_payload_change():
    obj1 = {"a": 1, "b": 2}
    obj2 = {"a": 1, "b": 3}
    obj3 = {"a": 1, "b": 2, "c": 3}

    fp1 = compute_fingerprint(obj1)
    fp2 = compute_fingerprint(obj2)
    fp3 = compute_fingerprint(obj3)

    assert fp1 != fp2
    assert fp1 != fp3
    assert fp2 != fp3


def test_fingerprint_ignores_dict_order():
    obj1 = {"a": 1, "b": 2}
    obj2 = {"b": 2, "a": 1}

    assert compute_fingerprint(obj1) == compute_fingerprint(obj2)


def test_reproducibility_across_processes(tmp_path):
    # This test verifies that the hash seed does not affect the fingerprint
    obj_str = '{"b": 2, "a": 1, "c": [3, 1, 2]}'

    script = f"""
import sys
from bender.core.serialization.fingerprint import compute_fingerprint
from bender.core.serialization.json import load_strict_json

obj = load_strict_json('{obj_str}')
print(compute_fingerprint(obj))
"""
    script_path = tmp_path / "test_script.py"
    script_path.write_text(script)

    env1 = os.environ.copy()
    env1["PYTHONHASHSEED"] = "1"

    env2 = os.environ.copy()
    env2["PYTHONHASHSEED"] = "2"

    res1 = subprocess.run(
        ["python", str(script_path)], env=env1, capture_output=True, text=True, check=True,
    )
    res2 = subprocess.run(
        ["python", str(script_path)], env=env2, capture_output=True, text=True, check=True,
    )

    assert res1.stdout.strip() == res2.stdout.strip()
