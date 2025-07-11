# 🪐 tasks.py - Celery tasks for fetching and publishing Star Wars planet data

import logging

import requests
from celery import shared_task
from pybreaker import CircuitBreaker, CircuitBreakerError

from publishers.kafka_publisher import KafkaPublisher

from .models import Planet

# -------------------------------------------------------------------
# ⚙️ Logger and circuit breaker setup
# -------------------------------------------------------------------

logger = logging.getLogger(__name__)
breaker = CircuitBreaker(fail_max=3, reset_timeout=60)

# -------------------------------------------------------------------
# 🌐 GraphQL API configuration
# -------------------------------------------------------------------

GRAPHQL_URL = "https://swapi-graphql.netlify.app/graphql"
GRAPHQL_QUERY = """
query {
  allPlanets {
    planets {
      name
      population
      terrains
      climates
    }
  }
}
"""

# -------------------------------------------------------------------
# 🚀 Celery Task: fetch_and_store_planets
# -------------------------------------------------------------------


@shared_task(bind=True, max_retries=2, default_retry_delay=30)
def fetch_and_store_planets(self):
    """
    Fetches all planets from the Star Wars GraphQL API, normalizes the data,
    and upserts it into the database with observability and retries.
    """
    try:
        r = breaker.call(
            requests.post,
            GRAPHQL_URL,
            json={"query": GRAPHQL_QUERY},
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()["data"]["allPlanets"]["planets"]

        for p in data:
            # Normalize population
            pop_raw = p.get("population")
            try:
                population = int(pop_raw)
            except (ValueError, TypeError):
                population = None

            terrains = p.get("terrains") or []
            climates = p.get("climates") or []

            Planet.objects.update_or_create(
                name=p["name"],
                defaults={
                    "population": population,
                    "terrains": terrains,
                    "climates": climates,
                },
            )

        logger.info("✅ fetch_and_store_planets completed successfully.")

    except CircuitBreakerError:
        logger.error("❌ Circuit breaker is open; skipping fetch_and_store_planets.")
    except Exception as exc:
        logger.error(f"❌ Error in fetch_and_store_planets: {exc}")
        raise self.retry(exc=exc)


# -------------------------------------------------------------------
# 🚀 Celery Task: publish_planet_event_task
# -------------------------------------------------------------------


@shared_task(ignore_result=True)
def publish_planet_event_task(event_type: str, data: dict):
    """
    Publishes a planet-related event to Kafka asynchronously.
    Executes in a worker, separate from Gunicorn.
    """
    KafkaPublisher.publish_planet_event(event_type, data)
