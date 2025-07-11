# analytics/urls.py

from django.urls import re_path

from .views import EventStatsView

urlpatterns = [
    # Accepts both /events/stats and /events/stats/
    re_path(r"^events/stats/?$", EventStatsView.as_view(), name="event-stats"),
]
