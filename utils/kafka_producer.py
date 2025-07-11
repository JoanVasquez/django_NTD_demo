# 🛰️ kafka_producer.py - Kafka event producer with OTEL + Prometheus monitoring

import json
import logging
import os
import time

from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
from opentelemetry import trace
from prometheus_client import Counter

# 🪵 Logger and tracer setup
logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)

# 📈 Prometheus counter for published events
events_published_counter = Counter(
    "kafka_events_published_total",
    "Total events published to Kafka",
    ["topic"],
)

# 🌐 Kafka configuration
KAFKA_BROKER_URL = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")


def _bootstrap_producer(retries: int = 3, delay: int = 2) -> KafkaProducer:
    """
    🔄 Attempt to create a KafkaProducer with retry logic for resilience.
    """
    attempt = 0
    while attempt < retries:
        try:
            return KafkaProducer(
                bootstrap_servers=[KAFKA_BROKER_URL],
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                retries=5,
                retry_backoff_ms=1000,
            )
        except NoBrokersAvailable:
            attempt += 1
            logger.warning(
                f"Kafka not available (attempt {attempt}/{retries}) "
                f"retrying in {delay}s..."
            )

            time.sleep(delay)
    raise RuntimeError("Kafka unreachable after several attempts")


# 💤 Lazy-initialized producer; do not connect at import time
_producer = None


def _get_producer() -> KafkaProducer:
    """
    🪄 Return the singleton Kafka producer, initializing if needed.
    """
    global _producer
    if _producer is None:
        _producer = _bootstrap_producer()
    return _producer


def publish_event(topic: str, event: dict) -> None:
    """
    🚀 Publish an event to Kafka with:
    • OTEL tracing for observability.
    • Prometheus metrics for monitoring.
    • Fire-and-forget sending for non-blocking publishing.
    """
    with tracer.start_as_current_span("publish_kafka_event") as span:
        span.set_attribute("messaging.system", "kafka")
        span.set_attribute("messaging.destination", topic)
        span.set_attribute("messaging.message_payload", str(event))

        producer = _get_producer()
        producer.send(topic, event)

        events_published_counter.labels(topic=topic).inc()
        logger.info(
            "✅ Event published",
            extra={"topic": topic, "event": event},
        )
