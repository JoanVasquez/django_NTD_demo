# 🪐 planet_event.py - PlanetEvent model for Kafka event consumption tracking

from django.db import models
from django.utils import timezone


class PlanetEvent(models.Model):
    """
    📡 Stores every planet event consumed from Kafka with:
    • event_type: type of the event consumed.
    • data: event payload as JSON.
    • consumed_at: timestamp when the event was processed.
    """

    event_type = models.CharField(max_length=50)
    data = models.JSONField()
    consumed_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        """
        Returns a readable representation:
        "<event_type> @ <consumed_at in ISO-8601>"
        """
        return f"{self.event_type} @ {self.consumed_at.isoformat()}"

    class Meta:
        indexes = [
            models.Index(fields=["consumed_at"]),
        ]
