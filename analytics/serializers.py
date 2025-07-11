# 📊 event_count_serializer.py - Serializer for event count analytics

from rest_framework import serializers


class EventCountSerializer(serializers.Serializer):
    """
    📈 Serializer for daily event count payloads with:
    • date: Date for the event count (YYYY-MM-DD).
    • count: Number of events (must be >= 0).
    """

    date = serializers.DateField()
    count = serializers.IntegerField(min_value=0)
