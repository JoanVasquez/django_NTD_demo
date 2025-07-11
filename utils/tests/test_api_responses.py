# ✅ test_api_responses.py - Tests for reusable API response utilities

import pytest
from rest_framework import status

from utils.rest_util import error_response, success_response

# ──────────────────────────────────────────────────────────────
# 🚀 Tests for success_response
# ──────────────────────────────────────────────────────────────


def test_success_defaults():
    """Test success_response with default parameters."""
    resp = success_response()
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data == {"status": "success", "data": None}


def test_success_with_payload_and_custom_status():
    """Test success_response with payload, message, and custom status."""
    data = {"id": 123, "name": "Naboo"}
    message = "Planet created"
    resp = success_response(
        data=data,
        message=message,
        status_code=status.HTTP_201_CREATED,
    )
    assert resp.status_code == status.HTTP_201_CREATED
    assert resp.data == {
        "status": "success",
        "data": data,
        "message": message,
    }


# ──────────────────────────────────────────────────────────────
# 🚨 Tests for error_response
# ──────────────────────────────────────────────────────────────


def test_error_defaults():
    """Test error_response with default parameters."""
    resp = error_response()
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.data == {"status": "error"}


def test_error_with_message_errors_and_custom_status():
    """Test error_response with message, errors, and custom status."""
    errors = {"name": ["This field is required."]}
    message = "Validation failed"
    resp = error_response(
        message=message,
        errors=errors,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert resp.data == {
        "status": "error",
        "message": message,
        "errors": errors,
    }


# ──────────────────────────────────────────────────────────────
# 🔄 Parametrized sanity checks
# ──────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "msg,errs,code",
    [
        (None, None, status.HTTP_400_BAD_REQUEST),
        ("Not found", None, status.HTTP_404_NOT_FOUND),
        ("Conflict", {"id": ["Duplicate"]}, status.HTTP_409_CONFLICT),
    ],
)
def test_error_parametrized(msg, errs, code):
    """Parametrized test for error_response with varied inputs."""
    resp = error_response(message=msg, errors=errs, status_code=code)
    body = resp.data

    assert resp.status_code == code
    assert body["status"] == "error"
    if msg:
        assert body["message"] == msg
    if errs:
        assert body["errors"] == errs
