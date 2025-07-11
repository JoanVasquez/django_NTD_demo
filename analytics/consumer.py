import json
import logging
import os
from datetime import datetime, timezone

import django
from kafka import KafkaConsumer
from kafka.errors import KafkaError

from analytics.models import PlanetEvent
from cache.cache_manager import CacheManager

# ───────────────────────────────────────────────────────────────────────────────
# 1) Bootstrap Django before importing any models
# ───────────────────────────────────────────────────────────────────────────────
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
django.setup()


# 📝 Setup logging
logger = logging.getLogger(__name__)


def run_consumer():
    # 🔌 Initialize Kafka consumer with configuration
    consumer = KafkaConsumer(
        "planet_events",
        bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092").split(","),
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="analytics-consumer",
    )

    logger.info("🔍 Starting analytics consumer…")
    # 🔄 Main consumer loop
    for msg in consumer:
        try:
            # 📥 Get event data from message
            evt = msg.value or {}

            # 💾 Step 1: Store raw event data in database for audit
            PlanetEvent.objects.create(
                event_type=evt.get("type", ""),
                data=evt.get("data", {}),
            )

            # 📊 Step 2: Increment counter in Redis for event date
            ts_ms = msg.timestamp or 0  # epoch ms
            day = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc).strftime(
                "%Y-%m-%d"
            )
            CacheManager._incr_event_count_for_day(day)

            # ✅ Log successful event processing
            logger.info("✅ Consumed event", extra={"event": evt})
        except (KafkaError, Exception) as e:
            # ❌ Log any errors that occur
            logger.error("❌ Error in consumer loop", exc_info=e)


# 🚀 Only run the consumer when executed as a script
if __name__ == "__main__":
    run_consumer()
