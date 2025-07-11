# ✅ rest_util.py - Utility helpers for consistent DRF API responses

from rest_framework import status
from rest_framework.response import Response

# ──────────────────────────────────────────────────────────────
# ✅ Success response helper
# ──────────────────────────────────────────────────────────────


def success_response(data=None, message=None, status_code=status.HTTP_200_OK):
    """
    ✅ Returns a DRF Response with:
    • status: "success"
    • data: payload (optional)
    • message: optional message
    • HTTP status code (default 200)
    """
    payload = {"status": "success", "data": data}
    if message:
        payload["message"] = message
    return Response(payload, status=status_code)


# ──────────────────────────────────────────────────────────────
# 🚨 Error response helper
# ──────────────────────────────────────────────────────────────


def error_response(message=None, errors=None, status_code=status.HTTP_400_BAD_REQUEST):
    """
    🚨 Returns a DRF Response with:
    • status: "error"
    • message: optional error message
    • errors: optional dictionary of field errors
    • HTTP status code (default 400)
    """
    payload = {"status": "error"}
    if message:
        payload["message"] = message
    if errors:
        payload["errors"] = errors
    return Response(payload, status=status_code)
