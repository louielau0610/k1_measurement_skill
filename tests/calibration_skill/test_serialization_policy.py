"""Serialization policy tests — canonical JSON, digests, NaN/Inf rejection."""
import json
import math
import hashlib
import pytest
from calibration_skill.schemas.codec import canonical_json_dumps
from calibration_skill.domain.calibration import _canonical_json, _content_digest


class TestCanonicalJson:
    def test_key_order_invariance(self):
        """Two objects with different key insertion order produce same canonical bytes."""
        a = {"b": 2, "a": 1}
        b = {"a": 1, "b": 2}
        assert canonical_json_dumps(a) == canonical_json_dumps(b)
        assert canonical_json_dumps(a) == '{"a":1,"b":2}'

    def test_key_order_invariance_produces_same_digest(self):
        a = {"b": 2, "a": 1}
        b = {"a": 1, "b": 2}
        d1 = hashlib.sha256(_canonical_json(a)).hexdigest()
        d2 = hashlib.sha256(_canonical_json(b)).hexdigest()
        assert d1 == d2

    def test_list_order_is_preserved(self):
        """Lists with different element order produce different canonical bytes."""
        a = {"items": [1, 2]}
        b = {"items": [2, 1]}
        assert canonical_json_dumps(a) != canonical_json_dumps(b)

    def test_list_order_produces_different_digest(self):
        a = {"items": [1, 2]}
        b = {"items": [2, 1]}
        d1 = hashlib.sha256(_canonical_json(a)).hexdigest()
        d2 = hashlib.sha256(_canonical_json(b)).hexdigest()
        assert d1 != d2, "Different list order must produce different digests"

    def test_no_whitespace(self):
        result = canonical_json_dumps({"a": 1, "b": [1, 2, 3]})
        assert " " not in result

    def test_nested_sorting(self):
        obj = {"z": {"c": 3, "a": 1}, "a": 1}
        result = canonical_json_dumps(obj)
        assert result == '{"a":1,"z":{"a":1,"c":3}}'

    def test_utf8_encoding(self):
        obj = {"message": "速度"}
        result = canonical_json_dumps(obj)
        assert "速度" in result


class TestContentDigest:
    def test_digest_is_sha256_hex(self):
        digest = _content_digest({"test": "value"})
        assert len(digest) == 64
        assert all(c in "0123456789abcdef" for c in digest)

    def test_identical_objects_produce_identical_digest(self):
        d1 = _content_digest({"a": 1, "b": 2})
        d2 = _content_digest({"b": 2, "a": 1})
        assert d1 == d2

    def test_different_objects_produce_different_digest(self):
        d1 = _content_digest({"a": 1})
        d2 = _content_digest({"a": 2})
        assert d1 != d2


class TestNaNInfRejection:
    def test_nan_in_dict_detected(self):
        from calibration_skill.schemas.codec import _check_no_nan_inf
        errors = _check_no_nan_inf({"value": float("nan")})
        assert len(errors) > 0

    def test_inf_in_dict_detected(self):
        from calibration_skill.schemas.codec import _check_no_nan_inf
        errors = _check_no_nan_inf({"value": float("inf")})
        assert len(errors) > 0

    def test_nan_in_list_detected(self):
        from calibration_skill.schemas.codec import _check_no_nan_inf
        errors = _check_no_nan_inf([1.0, float("nan"), 3.0])
        assert len(errors) > 0


class TestMonotonicTimeSerialization:
    def test_timestamps_serialize_as_integers(self):
        """Monotonic timestamps must be JSON integers, not floats."""
        data = {"issued_monotonic_ns": 1000, "expiry_monotonic_ns": 2000}
        result = canonical_json_dumps(data)
        parsed = json.loads(result)
        assert isinstance(parsed["issued_monotonic_ns"], int)
        assert parsed["issued_monotonic_ns"] == 1000
        # Confirm no decimal point
        assert "1000.0" not in result


class TestEnumSerialization:
    def test_enum_values_are_lowercase(self):
        from calibration_skill.domain.enums import RobotPlatform
        val = RobotPlatform.BOOSTER_K1.value
        assert val == "booster_k1"
        assert val.islower()
