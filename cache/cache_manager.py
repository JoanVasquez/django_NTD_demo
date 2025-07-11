# 🗄️ cache_manager.py - CacheManager for caching planets and analytics stats

from django.core.cache import cache


class CacheManager:
    # 🌍 Planets caching
    PLANET_CACHE_PREFIX = "planet:"
    ALL_PLANETS_CACHE_KEY = "planets:all"

    @staticmethod
    def get_planet_from_cache(planet_id: int):
        """Retrieve a single planet from cache or None."""
        key = f"{CacheManager.PLANET_CACHE_PREFIX}{planet_id}"
        return cache.get(key)

    @staticmethod
    def set_planet_in_cache(planet_id: int, data: dict, timeout: int = 300):
        """Cache a single planet with optional timeout."""
        key = f"{CacheManager.PLANET_CACHE_PREFIX}{planet_id}"
        cache.set(key, data, timeout=timeout)

    @staticmethod
    def invalidate_planet_cache(planet_id: int):
        """Remove a single planet from the cache."""
        key = f"{CacheManager.PLANET_CACHE_PREFIX}{planet_id}"
        cache.delete(key)

    @staticmethod
    def get_all_planets_from_cache():
        """Retrieve all cached planets or None."""
        return cache.get(CacheManager.ALL_PLANETS_CACHE_KEY)

    @staticmethod
    def set_all_planets_in_cache(data: list, timeout: int = 300):
        """Cache the list of all planets with optional timeout."""
        cache.set(CacheManager.ALL_PLANETS_CACHE_KEY, data, timeout=timeout)

    @staticmethod
    def invalidate_all_planets_cache():
        """Remove all planets from the cache."""
        cache.delete(CacheManager.ALL_PLANETS_CACHE_KEY)

    # 📊 Analytics event stats caching
    ANALYTICS_STATS_CACHE_KEY = "analytics:events_stats"

    @staticmethod
    def get_event_stats_from_cache():
        """Retrieve cached analytics event-stats list or None."""
        return cache.get(CacheManager.ANALYTICS_STATS_CACHE_KEY)

    @staticmethod
    def set_event_stats_in_cache(data: list, timeout: int = 300):
        """Cache analytics event-stats list with optional timeout."""
        cache.set(CacheManager.ANALYTICS_STATS_CACHE_KEY, data, timeout=timeout)

    @staticmethod
    def invalidate_event_stats_cache():
        """Remove analytics event-stats cache."""
        cache.delete(CacheManager.ANALYTICS_STATS_CACHE_KEY)

    @staticmethod
    def _incr_event_count_for_day(day_str: str):
        """
        Increment (+1) the event count for a given day.

        Keeps the format:
        [{'date': 'YYYY-MM-DD', 'count': N}, ...]
        used by get/set_event_stats_in_cache.
        """
        stats = cache.get(CacheManager.ANALYTICS_STATS_CACHE_KEY) or []
        tmp = {row["date"]: row["count"] for row in stats}
        tmp[day_str] = tmp.get(day_str, 0) + 1
        new_stats = [{"date": d, "count": c} for d, c in sorted(tmp.items())]
        cache.set(CacheManager.ANALYTICS_STATS_CACHE_KEY, new_stats, timeout=None)
