# ✅ test_base_exception.py - Tests for BaseAppException behavior and formatting

import pytest

from utils.exceptions import BaseAppException

# ──────────────────────────────────────────────────────────────
# 🚨 Tests: Basic behavior of BaseAppException
# ──────────────────────────────────────────────────────────────


def test_defaults():
    """Test BaseAppException with default status and payload."""
    exc = BaseAppException("something went wrong")
    assert exc.message == "something went wrong"
    assert exc.status_code == 400
    assert exc.payload == {}
    assert exc.to_dict() == {
        "status": "error",
        "message": "something went wrong",
    }


def test_custom_status_and_payload():
    """Test BaseAppException with custom status and payload."""
    payload = {"field": "name", "code": "duplicate"}
    exc = BaseAppException(
        "Planet already exists",
        status_code=409,
        payload=payload,
    )
    assert exc.status_code == 409
    assert exc.payload == payload

    expected = {
        "status": "error",
        "message": "Planet already exists",
        "field": "name",
        "code": "duplicate",
    }
    assert exc.to_dict() == expected


# ──────────────────────────────────────────────────────────────
# 🔄 Parametrized tests for diverse payloads and statuses
# ──────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "msg,status,payload",
    [
        ("Bad request", 400, {}),
        ("Not found", 404, {"resource": "Planet"}),
        ("Conflict", 409, {"id": 99}),
    ],
)
def test_parametrized(msg, status, payload):
    """Parametrized test for BaseAppException with varied inputs."""
    exc = BaseAppException(msg, status, payload)
    body = exc.to_dict()

    assert body["message"] == msg
    assert exc.status_code == status
    assert body["status"] == "error"

    for key, value in payload.items():
        assert body[key] == value
