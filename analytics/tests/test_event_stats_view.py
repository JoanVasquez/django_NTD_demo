# 📊 test_event_stats_view.py - Tests for EventStatsView analytics endpoint

import datetime as dt

from rest_framework import status
from rest_framework.test import APIRequestFactory

from analytics.views import EventStatsView

# 🚀 Reusable APIRequestFactory instance for clean test requests
factory = APIRequestFactory()


def _as_view():
    """Return the standard callable view for EventStatsView."""
    return EventStatsView.as_view()


def test_get_event_stats_success(mocker):
    """
    ✅ Tests that GET /analytics/stats/:
    • Returns 200 OK.
    • Returns 'success' status.
    • Returns correct dummy event stats from the service.
    """
    today = dt.date.today()
    dummy_stats = [
        {"date": str(today - dt.timedelta(days=2)), "count": 3},
        {"date": str(today - dt.timedelta(days=1)), "count": 7},
        {"date": str(today), "count": 2},
    ]

    # Patch the AnalyticsService method inside the view module
    mocker.patch(
        "analytics.views.AnalyticsService.get_event_counts_by_date",
        return_value=dummy_stats,
    )

    # Execute request
    request = factory.get("/analytics/stats/")
    response = _as_view()(request)

    # Assertions
    assert response.status_code == status.HTTP_200_OK
    assert response.data["status"] == "success"
    assert response.data["data"] == dummy_stats
