# 🪐 serializers.py - DRF serializer for Planet model

from rest_framework import serializers

from planets.models import Planet


class PlanetSerializer(serializers.ModelSerializer):
    """
    Serializer for Planet objects, exposing relevant fields while enforcing
    read-only constraints on database-managed fields.
    """

    class Meta:
        model = Planet
        fields = [
            "id",
            "name",
            "population",
            "terrains",
            "climates",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
