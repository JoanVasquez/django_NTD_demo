# 🛡️ test_error_handler_middleware.py - Tests for error handler middleware

import importlib
import json
import types

import pytest
from django.http import JsonResponse
from django.test.client import RequestFactory

# -------------------------------------------------------------------
# 🛠️ Helpers
# -------------------------------------------------------------------

factory = RequestFactory()


class _DummySpan:
    """
    Lightweight OTEL span substitute for testing without requiring OTEL.
    """

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        pass

    def set_attribute(self, *a, **kw):
        pass

    def record_exception(self, *a, **kw):
        pass


def _make_middleware():
    """
    Instantiates the real middleware while patching tracer and logger
    to avoid requiring OTEL or logging noise during tests.
    """
    mw_mod = importlib.import_module("core.middleware.centralized_error_handler")
    mw_mod.tracer.start_as_current_span = lambda *a, **k: _DummySpan()
    mw_mod.logger = types.SimpleNamespace(
        warning=lambda *a, **k: None,
        error=lambda *a, **k: None,
    )
    return mw_mod.CentralizedErrorHandlerMiddleware(lambda r: JsonResponse({}))


# -------------------------------------------------------------------
# ✅ 1) Handles BaseAppException → JSON 4xx with provided payload
# -------------------------------------------------------------------


def test_base_app_exception_handled():
    from utils.exceptions import BaseAppException

    exc = BaseAppException(
        "bad-request",
        status_code=422,
        payload={"foo": "bar"},
    )

    mw = _make_middleware()
    request = factory.get("/dummy/")

    response = mw.process_exception(request, exc)

    assert response.status_code == 422
    body = json.loads(response.content)
    assert body == {"status": "error", "message": "bad-request", "foo": "bar"}


# -------------------------------------------------------------------
# ✅ 2) Handles generic exceptions → JSON 500 with generic message
# -------------------------------------------------------------------


def test_generic_exception_handled():
    class Boom(RuntimeError):
        pass

    mw = _make_middleware()
    request = factory.post("/dummy/")

    response = mw.process_exception(request, Boom("💥"))

    assert response.status_code == 500
    body = json.loads(response.content)
    assert body == {
        "status": "error",
        "message": "An internal server error occurred. Please contact support.",
    }
