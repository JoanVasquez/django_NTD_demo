# 🛰️ test_kafka_publisher.py - Tests for KafkaPublisher

import pytest

from publishers.kafka_publisher import KafkaPublisher


def _make_event(event_type: str, data: dict) -> dict:
    """
    Utility to generate a structured Kafka event payload.
    """
    return {"type": event_type, "data": data}


# -------------------------------------------------------------------
# ✅ Test: publish_planet_event - success path
# -------------------------------------------------------------------


def test_publish_planet_event_success(mocker):
    """
    Should call publish_event with correct parameters and log success.
    """
    event_type = "created"
    data = {"id": 1, "name": "Naboo"}

    mocked_publish = mocker.patch("publishers.kafka_publisher.publish_event")
    mocked_logger = mocker.patch("publishers.kafka_publisher.logger")

    KafkaPublisher.publish_planet_event(event_type, data)

    mocked_publish.assert_called_once_with(
        "planet_events", _make_event(event_type, data)
    )

    mocked_logger.info.assert_called()
    _, log_kwargs = mocked_logger.info.call_args
    assert log_kwargs["extra"]["event_type"] == event_type
    assert log_kwargs["extra"]["data"] == data


# -------------------------------------------------------------------
# ❌ Test: publish_planet_event - failure path
# -------------------------------------------------------------------


def test_publish_planet_event_failure(mocker):
    """
    Should log an error and re-raise if publish_event fails.
    """
    event_type = "deleted"
    data = {"id": 99}

    err = RuntimeError("Kafka down")
    mocker.patch("publishers.kafka_publisher.publish_event", side_effect=err)
    mocked_logger = mocker.patch("publishers.kafka_publisher.logger")

    with pytest.raises(RuntimeError):
        KafkaPublisher.publish_planet_event(event_type, data)

    mocked_logger.error.assert_called()
    _, log_kwargs = mocked_logger.error.call_args
    assert log_kwargs["extra"]["event_type"] == event_type
    assert "error" in log_kwargs["extra"]
