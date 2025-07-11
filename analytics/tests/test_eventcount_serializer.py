# 🧪 test_event_count_serializer.py - Tests for EventCountSerializer

import datetime as dt

import pytest

from analytics.serializers import EventCountSerializer

# -------------------------------------------------------------------
# ✅ 1) Correct serialization of a valid record
# -------------------------------------------------------------------


def test_event_count_serializer_valid():
    """
    Tests that a valid payload with date and count serializes correctly
    and returns validated data unchanged.
    """
    payload = {"date": dt.date(2024, 1, 1), "count": 5}

    ser = EventCountSerializer(data=payload)
    assert ser.is_valid(), ser.errors
    assert ser.validated_data == payload


# -------------------------------------------------------------------
# 🚨 2) Validation with negative 'count' raises error
# -------------------------------------------------------------------


def test_event_count_serializer_negative_count():
    """
    Tests that providing a negative 'count' results in a validation error.
    """
    bad_payload = {"date": dt.date.today(), "count": -1}

    ser = EventCountSerializer(data=bad_payload)
    assert not ser.is_valid()
    assert "count" in ser.errors
    assert ser.errors["count"][0].code == "min_value"


# -------------------------------------------------------------------
# 🚨 3) Validation with missing required fields raises error
# -------------------------------------------------------------------


@pytest.mark.parametrize("missing_key", ["date", "count"])
def test_event_count_serializer_required_fields(missing_key):
    """
    Tests that omitting required fields ('date' or 'count') results in
    validation errors for those fields with the 'required' error code.
    """
    data = {"date": dt.date.today(), "count": 3}
    data.pop(missing_key)

    ser = EventCountSerializer(data=data)
    assert not ser.is_valid()
    assert missing_key in ser.errors
    assert ser.errors[missing_key][0].code == "required"
