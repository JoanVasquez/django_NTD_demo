# 🧪 test_analytics_consumer.py - Tests for analytics.consumer

import importlib
import types
from datetime import datetime, timedelta, timezone

# -------------------------------------------------------------------
# 🛠️ Dummy utilities / stubs for KafkaConsumer tests
# -------------------------------------------------------------------


def _ts_ms(days_offset: int) -> int:
    """
    Return epoch-ms for midnight UTC today plus the specified day offset.
    Used for simulating Kafka message timestamps.
    """
    ts = datetime.now(tz=timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    ) + timedelta(days=days_offset)
    return int(ts.timestamp() * 1000)


class _DummyMsg:
    """Kafka message stub with `value` and `timestamp` fields."""

    def __init__(self, value, ts_ms):
        self.value = value
        self.timestamp = ts_ms


class _DummyKafkaConsumer:
    """
    In-memory KafkaConsumer substitute for controlled iteration.
    """

    def __init__(self, *args, **kwargs):
        self._msgs = [
            _DummyMsg({"type": "created", "data": {"id": 1}}, _ts_ms(-2)),
            _DummyMsg({"type": "deleted", "data": {"id": 99}}, _ts_ms(-1)),
        ]

    def __iter__(self):
        return iter(self._msgs)


# -------------------------------------------------------------------
# ✅ 1) Happy path test
# -------------------------------------------------------------------


def test_run_consumer_success(mocker):
    """
    Tests that `run_consumer`:
    • Consumes messages.
    • Creates PlanetEvent entries.
    • Calls CacheManager increment.
    """
    consumer_mod = importlib.import_module("analytics.consumer")

    # Patch KafkaConsumer with the in-memory stub
    mocker.patch.object(consumer_mod, "KafkaConsumer", _DummyKafkaConsumer)

    # Capture calls to PlanetEvent.objects.create
    created_calls = []
    consumer_mod.PlanetEvent.objects = types.SimpleNamespace(
        create=lambda **kw: created_calls.append(kw)
    )

    # Capture calls to CacheManager._incr_event_count_for_day
    incr_calls = []
    mocker.patch.object(
        consumer_mod.CacheManager,
        "_incr_event_count_for_day",
        side_effect=lambda d: incr_calls.append(d),
    )

    # Silence logger during test
    mocker.patch.object(consumer_mod, "logger")

    # Execute
    consumer_mod.run_consumer()

    # Assertions
    assert len(created_calls) == 2
    assert {c["event_type"] for c in created_calls} == {"created", "deleted"}
    assert len(incr_calls) == 2
    assert all(len(day) == 10 for day in incr_calls)  # checks 'YYYY-MM-DD'


# -------------------------------------------------------------------
# 🚨 2) Error path test
# -------------------------------------------------------------------


def test_run_consumer_error_path(mocker):
    """
    Tests that `run_consumer` logs an error when PlanetEvent creation fails.
    """
    consumer_mod = importlib.import_module("analytics.consumer")

    # Consumer returning a single message
    consumer_mod.KafkaConsumer = lambda *a, **k: [_DummyMsg({"type": "X"}, _ts_ms(0))]

    # PlanetEvent.objects.create raises an exception
    err = RuntimeError("DB down")
    consumer_mod.PlanetEvent.objects = types.SimpleNamespace(
        create=lambda **kw: (_ for _ in ()).throw(err)
    )

    # Mock logger to capture error logging
    mocked_logger = mocker.patch.object(consumer_mod, "logger")

    # Patch CacheManager increment
    mocker.patch.object(consumer_mod.CacheManager, "_incr_event_count_for_day")

    # Execute
    consumer_mod.run_consumer()

    # Assertions
    mocked_logger.error.assert_called()
    assert "Error in consumer loop" in mocked_logger.error.call_args[0][0]
