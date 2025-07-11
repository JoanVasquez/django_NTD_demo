# 🧩 test_urls.py - Tests for EventStatsView route and resolution

import datetime as dt
import importlib
import sys
import types

from django.conf import settings
from django.test import RequestFactory
from django.urls import path, resolve, reverse

# -------------------------------------------------------------------
# 🛠️ 1) Minimal DRF stubs if rest_framework is not installed
# -------------------------------------------------------------------
if "rest_framework" not in sys.modules:
    rf_views = types.ModuleType("rest_framework.views")

    class _StubAPIView:
        authentication_classes = ()
        permission_classes = ()
        throttle_classes = ()

        @classmethod
        def as_view(cls, **initkwargs):
            def _fake_view(request, *args, **kwargs):
                self = cls()
                return self.dispatch(request, *args, **kwargs)

            _fake_view.__name__ = "_FakeView"
            _fake_view.view_class = cls
            return _fake_view

        def dispatch(self, request, *args, **kw):
            handler = getattr(self, request.method.lower(), None)
            return handler(request, *args, **kw)

    rf_views.APIView = _StubAPIView

    rf_resp = types.ModuleType("rest_framework.response")

    class _StubResponse(dict):
        def __init__(self, data, status=200):
            super().__init__(data)
            self.status_code = status
            self.data = data

    rf_resp.Response = _StubResponse

    rf_root = types.ModuleType("rest_framework")
    rf_root.views = rf_views
    rf_root.response = rf_resp

    sys.modules.update(
        {
            "rest_framework": rf_root,
            "rest_framework.views": rf_views,
            "rest_framework.response": rf_resp,
        }
    )

# -------------------------------------------------------------------
# ⚙️ 2) Load URLCONF (with stubs if applicable)
# -------------------------------------------------------------------
URLCONF = settings.ROOT_URLCONF or "app.urls"
importlib.import_module(URLCONF)

from analytics.views import EventStatsView  # noqa: E402

factory = RequestFactory()

# -------------------------------------------------------------------
# 🛠️ 3) Helper to extract payload from stub or real DRF Response
# -------------------------------------------------------------------


def _payload(resp):
    """
    Return the JSON payload dictionary from the response,
    regardless of whether it is a stub or DRF Response.
    """
    if isinstance(resp, dict):
        return resp
    return resp.data


# -------------------------------------------------------------------
# ✅ 4) Test route resolution and view response
# -------------------------------------------------------------------


def test_event_stats_route_and_view(mocker):
    """
    🚀 Tests:
    • URL /events/stats/ resolves to 'event-stats' view name.
    • View returns 200 with {'status': 'success', 'data': ...}.
    """
    dummy_stats = [{"date": str(dt.date.today()), "count": 5}]
    mocker.patch(
        "analytics.views.AnalyticsService.get_event_counts_by_date",
        return_value=dummy_stats,
    )

    url = reverse("event-stats")
    match = resolve(url)

    # ✓ Assert the URL resolves to the correct view
    assert match.func.view_class is EventStatsView

    # Direct invocation of the view
    request = factory.get(url)
    response = match.func(request)

    assert response.status_code == 200
    body = _payload(response)
    assert body["status"] == "success"
    assert body["data"] == dummy_stats
