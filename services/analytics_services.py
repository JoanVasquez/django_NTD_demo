# 📈 analytics_services.py - Provides analytics services for event stats

from django.db.models import Count
from django.db.models.functions import TruncDate

from analytics.models import PlanetEvent
from cache.cache_manager import CacheManager


class AnalyticsService:
    """
    Service layer for analytics logic related to PlanetEvent statistics.
    """

    @staticmethod
    def get_event_counts_by_date():
        """
        Retrieves the count of planet events grouped by day.

        1️⃣ Tries cache first.
        2️⃣ If cache miss, queries the DB, transforms results, caches them, and returns.
        """
        # 🔍 Try cache first
        stats = CacheManager.get_event_stats_from_cache()
        if stats is not None:
            return stats

        # ❌ Cache miss: query DB for aggregated event counts by day
        qs = (
            PlanetEvent.objects.annotate(day=TruncDate("consumed_at"))
            .values("day")
            .annotate(count=Count("id"))
            .order_by("day")
        )

        stats = [{"date": str(item["day"]), "count": item["count"]} for item in qs]

        # 💾 Cache the result for subsequent calls (5-minute TTL)
        CacheManager.set_event_stats_in_cache(stats, timeout=300)

        return stats
