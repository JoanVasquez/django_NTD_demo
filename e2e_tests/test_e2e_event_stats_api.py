# 📊 test_e2e_event_stats_api.py - E2E tests for event stats aggregation API

from datetime import datetime, timezone

import pytest
from django.core.cache import cache
from django.urls import reverse

from analytics.models import PlanetEvent
from cache.cache_manager import CacheManager


@pytest.mark.django_db
def test_get_event_stats_aggregates_by_day(client):
    """
    Tests that:
    1) Event stats are aggregated correctly by day.
    2) Results are cached and returned consistently.
    """

    # 🧹 Ensure a clean table and clear cache
    PlanetEvent.objects.all().delete()
    cache.delete(CacheManager.ANALYTICS_STATS_CACHE_KEY)

    # 🪐 Create three events: two on 2025-01-01, one on 2025-01-02
    PlanetEvent.objects.create(
        event_type="created",
        consumed_at=datetime(2025, 1, 1, 10, 0, tzinfo=timezone.utc),
        data={"foo": "bar"},
    )
    PlanetEvent.objects.create(
        event_type="deleted",
        consumed_at=datetime(2025, 1, 1, 15, 30, tzinfo=timezone.utc),
        data={"baz": 123},
    )
    PlanetEvent.objects.create(
        event_type="updated",
        consumed_at=datetime(2025, 1, 2, 9, 45, tzinfo=timezone.utc),
        data={"hello": "world"},
    )

    url = reverse("event-stats")

    # 🚀 First call: calculates and caches the result
    resp1 = client.get(url)
    assert resp1.status_code == 200
    body1 = resp1.json()
    assert body1["status"] == "success"

    expected = [
        {"date": "2025-01-01", "count": 2},
        {"date": "2025-01-02", "count": 1},
    ]
    assert body1["data"] == expected

    # ⚡ Second call: should return cached data (same payload)
    resp2 = client.get(url)
    assert resp2.status_code == 200
    assert resp2.json() == body1
