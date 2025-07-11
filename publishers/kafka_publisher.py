# 🌐 kafka_publisher.py - Kafka event publisher for Planet events

import logging

from utils.kafka_producer import publish_event

# 🪵 Logger initialization
logger = logging.getLogger(__name__)


class KafkaPublisher:
    """
    📡 Handles publishing events to Kafka for the Planet domain.
    """

    @staticmethod
    def publish_planet_event(event_type: str, data: dict):
        """
        🚀 Publishes a Planet event to the 'planet_events' Kafka topic.
        Logs success and error states with structured metadata for observability.
        """
        event = {
            "type": event_type,
            "data": data,
        }
        try:
            publish_event("planet_events", event)
            logger.info(
                "✅ Published Planet event to Kafka",
                extra={
                    "event_type": event_type,
                    "topic": "planet_events",
                    "data": data,
                },
            )
        except Exception as e:
            logger.error(
                "❌ Failed to publish Planet event to Kafka",
                extra={
                    "event_type": event_type,
                    "topic": "planet_events",
                    "data": data,
                    "error": str(e),
                },
            )
            # Optionally re-raise for handling in the service layer if needed
            raise
