# 🪐 models.py - Planet model for Star Wars planets

from django.db import models


class Planet(models.Model):
    """
    Represents Star Wars planet data within the system.
    """

    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Name of the planet (must be unique).",
    )
    population = models.IntegerField(
        null=True,
        blank=True,
        help_text="Population of the planet (nullable).",
    )
    terrains = models.JSONField(
        default=list,
        blank=True,
        help_text="List of terrain types for the planet.",
    )
    climates = models.JSONField(
        default=list,
        blank=True,
        help_text="List of climate types for the planet.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the planet entry was created.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the planet entry was last updated.",
    )

    def __str__(self):
        """Return a readable string representation of the planet."""
        return f"{self.name} (Population: {self.population})"
