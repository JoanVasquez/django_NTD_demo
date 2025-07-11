# 📊 event_stats_view.py - EventStatsView for daily planet event counts

from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from services.analytics_services import AnalyticsService

from .serializers import EventCountSerializer


class EventStatsView(APIView):
    """
    📈 API endpoint that returns daily counts of planet events consumed.
    """

    @extend_schema(
        summary="Get planet-event counts by day",
        responses={200: EventCountSerializer(many=True)},
    )
    def get(self, request):
        """
        Handles GET requests to fetch daily event counts with a success status
        and a list of date/count pairs.
        """
        stats = AnalyticsService.get_event_counts_by_date()
        return Response({"status": "success", "data": stats})
