# 🗄️ test_cache_manager.py - Unit tests for CacheManager caching behavior

from datetime import date

import pytest

from cache.cache_manager import CacheManager

# -------------------------------------------------------------------
# 🧪 Dummy cache backend to replace django.core.cache for tests
# -------------------------------------------------------------------


class DummyCache(dict):
    """Implements only the methods CacheManager uses."""

    def get(self, key, default=None):
        return super().get(key, default)

    def set(self, key, value, timeout=None):
        # Ignore timeout for unit tests
        self[key] = value

    def delete(self, key):
        self.pop(key, None)


# -------------------------------------------------------------------
# 🛠️ Fixture: patch cache with DummyCache for all tests
# -------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _patch_cache(mocker):
    """
    Replaces the 'cache' imported in cache.cache_manager with DummyCache
    for all tests.
    """
    dummy = DummyCache()
    mocker.patch("cache.cache_manager.cache", dummy)
    return dummy


# -------------------------------------------------------------------
# ✅ Planet cache tests
# -------------------------------------------------------------------


def test_planet_cache_set_get_invalidate():
    """Tests caching, retrieving, and invalidating a single planet."""
    CacheManager.set_planet_in_cache(1, {"foo": "bar"})
    assert CacheManager.get_planet_from_cache(1) == {"foo": "bar"}

    CacheManager.invalidate_planet_cache(1)
    assert CacheManager.get_planet_from_cache(1) is None


def test_all_planets_cache_set_get_invalidate():
    """Tests caching, retrieving, and invalidating all planets."""
    CacheManager.set_all_planets_in_cache([{"id": 1}, {"id": 2}])
    assert CacheManager.get_all_planets_from_cache() == [{"id": 1}, {"id": 2}]

    CacheManager.invalidate_all_planets_cache()
    assert CacheManager.get_all_planets_from_cache() is None


# -------------------------------------------------------------------
# ✅ Analytics event stats cache tests
# -------------------------------------------------------------------


def test_event_stats_cache_set_get_invalidate():
    """Tests caching, retrieving, and invalidating event stats."""
    stats = [{"date": "2025-07-10", "count": 3}]
    CacheManager.set_event_stats_in_cache(stats)
    assert CacheManager.get_event_stats_from_cache() == stats

    CacheManager.invalidate_event_stats_cache()
    assert CacheManager.get_event_stats_from_cache() is None


def test_incr_event_count_for_day_new_key():
    """Tests incrementing count for a day with no existing entry."""
    day = date.today().isoformat()
    CacheManager.invalidate_event_stats_cache()  # ensure clean state

    CacheManager._incr_event_count_for_day(day)
    assert CacheManager.get_event_stats_from_cache() == [{"date": day, "count": 1}]


def test_incr_event_count_for_day_existing_key():
    """Tests incrementing count for a day with an existing entry."""
    day = "2025-07-10"
    CacheManager.set_event_stats_in_cache([{"date": day, "count": 2}])

    CacheManager._incr_event_count_for_day(day)
    CacheManager._incr_event_count_for_day(day)

    assert CacheManager.get_event_stats_from_cache() == [{"date": day, "count": 4}]
