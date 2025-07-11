# ✅ test_kafka_producer.py - Unit tests for utils.kafka_producer

import types

import pytest

import utils.kafka_producer as kp

# ──────────────────────────────────────────────────────────────
# 🧪 Stubs / Dummies for isolation
# ──────────────────────────────────────────────────────────────


class DummyProducer:
    """🛰️ Mimics kafka.KafkaProducer, records sent messages."""

    def __init__(self, *_, **__):
        self.sent = []  # [(topic, value)]

    def send(self, topic, value):
        self.sent.append((topic, value))


class DummySpan:
    """🔍 Minimal OTEL span context manager exposing set_attribute."""

    def __init__(self):
        self.attrs = {}

    def set_attribute(self, key, value):
        self.attrs[key] = value

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class DummyCounter:
    """📈 Mimics Prometheus Counter with labels().inc() tracking."""

    def __init__(self):
        self.inc_calls = []

    def labels(self, **labels):
        self._labels = labels
        return self

    def inc(self):
        self.inc_calls.append(self._labels)


# ──────────────────────────────────────────────────────────────
# ✅ Tests: publish_event
# ──────────────────────────────────────────────────────────────


def test_publish_event_success(mocker):
    """
    ✅ Ensures:
    • Producer.send() is called with topic + event.
    • Prometheus counter is incremented.
    • OTEL attributes are recorded on the span.
    """
    dummy_producer = DummyProducer()
    dummy_counter = DummyCounter()
    dummy_span = DummySpan()

    mocker.patch.object(kp, "_get_producer", return_value=dummy_producer)
    mocker.patch.object(kp, "events_published_counter", dummy_counter)
    mocker.patch.object(kp.tracer, "start_as_current_span", return_value=dummy_span)

    event = {"foo": "bar"}
    kp.publish_event("planet_events", event)

    assert dummy_producer.sent == [("planet_events", event)]
    assert dummy_counter.inc_calls == [{"topic": "planet_events"}]
    assert dummy_span.attrs["messaging.system"] == "kafka"
    assert dummy_span.attrs["messaging.destination"] == "planet_events"


# ──────────────────────────────────────────────────────────────
# ✅ Tests: _bootstrap_producer
# ──────────────────────────────────────────────────────────────


def test_bootstrap_producer_success(mocker):
    """✅ Returns a producer instance when KafkaProducer succeeds."""
    mocker.patch("utils.kafka_producer.KafkaProducer", DummyProducer)
    prod = kp._bootstrap_producer(retries=1)
    assert isinstance(prod, DummyProducer)


def test_bootstrap_producer_exhausted(mocker):
    """
    🚨 If KafkaProducer keeps raising NoBrokersAvailable after 'retries',
    raises RuntimeError after exhausting attempts.
    """

    class _Boom(Exception):
        """Simulated exception instead of importing the real one."""

    def _raise(*_, **__):
        raise _Boom

    mocker.patch("utils.kafka_producer.KafkaProducer", side_effect=_raise)
    mocker.patch("utils.kafka_producer.NoBrokersAvailable", _Boom)

    with pytest.raises(RuntimeError, match="Kafka unreachable"):
        kp._bootstrap_producer(retries=2, delay=0)
