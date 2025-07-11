# 🪐 test_planet_event_model.py - Tests for the PlanetEvent model

from datetime import datetime, timezone

from django.db import models

from analytics.models import PlanetEvent

# -------------------------------------------------------------------
# ✅ 1) __str__ includes event type + ISO-8601 consumed_at timestamp
# -------------------------------------------------------------------


def test_planet_event_str():
    """
    Tests that the __str__ method returns:
    "<event_type> @ <consumed_at in ISO-8601>"
    """
    ts = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    ev = PlanetEvent(event_type="created", data={}, consumed_at=ts)

    assert str(ev) == "created @ 2024-01-01T12:00:00+00:00"


# -------------------------------------------------------------------
# ✅ 2) The model has an index on the 'consumed_at' field
# -------------------------------------------------------------------


def test_planet_event_has_consumed_at_index():
    """
    Tests that PlanetEvent defines an index on the 'consumed_at' field
    for efficient querying and sorting.
    """
    indexes = PlanetEvent._meta.indexes
    assert any(
        isinstance(idx, models.Index) and idx.fields == ["consumed_at"]
        for idx in indexes
    ), (
        "PlanetEvent should have an Index(fields=['consumed_at']) "
        "defined in Meta.indexes"
    )
