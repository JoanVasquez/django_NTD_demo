# 📊 test_analytics_service.py - Tests for AnalyticsService

from unittest.mock import MagicMock

from services.analytics_services import AnalyticsService

# -------------------------------------------------------------------
# ✅ Test: Cache HIT
# -------------------------------------------------------------------


def test_get_event_counts_cache_hit(mocker):
    """
    Should return cached stats and avoid DB calls when cache HIT occurs.
    """
    cached_stats = [{"date": "2024-01-01", "count": 5}]

    mocker.patch(
        "services.analytics_services.CacheManager.get_event_stats_from_cache",
        return_value=cached_stats,
    )

    pe_mock = mocker.patch("services.analytics_services.PlanetEvent")

    result = AnalyticsService.get_event_counts_by_date()

    assert result == cached_stats
    pe_mock.objects.annotate.assert_not_called()


# -------------------------------------------------------------------
# ✅ Test: Cache MISS, fallback to DB
# -------------------------------------------------------------------


def test_get_event_counts_cache_miss(mocker):
    """
    Should fetch from DB, format correctly, and store in cache on cache MISS.
    """
    # 1️⃣ Cache MISS
    mocker.patch(
        "services.analytics_services.CacheManager.get_event_stats_from_cache",
        return_value=None,
    )

    # 2️⃣ Prepare simulated queryset chain
    qs_result = [
        {"day": "2024-01-01", "count": 3},
        {"day": "2024-01-02", "count": 1},
    ]

    dummy_manager = MagicMock()
    dummy_manager.annotate.return_value = dummy_manager
    dummy_manager.values.return_value = dummy_manager
    dummy_manager.order_by.return_value = qs_result

    mocker.patch(
        "services.analytics_services.PlanetEvent",
        **{"objects": dummy_manager},
    )

    # 3️⃣ Patch cache setter to confirm cache storage
    set_cache = mocker.patch(
        "services.analytics_services.CacheManager.set_event_stats_in_cache"
    )

    expected = [
        {"date": "2024-01-01", "count": 3},
        {"date": "2024-01-02", "count": 1},
    ]

    result = AnalyticsService.get_event_counts_by_date()

    assert result == expected
    set_cache.assert_called_once_with(expected, timeout=300)
