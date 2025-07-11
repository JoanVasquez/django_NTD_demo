# 🌍 planet_service.py - PlanetService with caching, DB orchestration, Celery events

import logging

from cache.cache_manager import CacheManager
from planets.tasks import publish_planet_event_task
from repositories.planet_repository import PlanetRepository
from utils.exceptions import BaseAppException

# 🪵 Logger initialization
logger = logging.getLogger(__name__)


class PlanetService:
    """
    🚀 Orchestrates CRUD operations for Planet entities using:
    • CacheManager for caching strategies
    • PlanetRepository for DB persistence
    • Celery for background event publishing
    """

    @staticmethod
    def list_all_planets():
        """📜 List all planets with caching, falling back to DB if cache misses."""
        logger.info("🔍 Fetching all planets")

        # 1️⃣ Check full-list cache
        cached = CacheManager.get_all_planets_from_cache()
        if cached is not None:
            logger.info("✅ Cache hit for all planets")
            return cached

        # 2️⃣ Cache miss: query DB
        planets_qs = PlanetRepository.list_all()
        data = [
            {
                "id": p.id,
                "name": p.name,
                "population": p.population,
                "climates": p.climates,
                "terrains": p.terrains,
            }
            for p in planets_qs
        ]
        logger.info(
            "✅ Fetched planets from DB",
            extra={"planet_count": len(data)},
        )

        # 3️⃣ Store in cache
        CacheManager.set_all_planets_in_cache(data)
        return data

    @staticmethod
    def create_planet(data: dict):
        """🛠️ Create a new planet and queue event for background processing."""
        logger.info("🛠️ Creating new planet", extra={"data": data})
        planet = PlanetRepository.create(data)

        # Invalidate full-list cache
        CacheManager.invalidate_all_planets_cache()

        # Queue event (non-blocking) via Celery
        publish_planet_event_task.delay(
            "created",
            {
                "id": planet.id,
                "name": planet.name,
                "population": planet.population,
                "climates": planet.climates,
                "terrains": planet.terrains,
            },
        )
        logger.info(
            "✅ Planet created (queued event)",
            extra={"planet_id": planet.id},
        )

        return {
            "id": planet.id,
            "name": planet.name,
            "population": planet.population,
            "climates": planet.climates,
            "terrains": planet.terrains,
        }

    @staticmethod
    def get_planet_by_id(planet_id: int):
        """🔍 Retrieve a single planet by ID with per-item caching."""
        id_int = int(planet_id)
        logger.info("🔍 Fetching planet", extra={"planet_id": id_int})

        # 1️⃣ Check per-item cache
        cached = CacheManager.get_planet_from_cache(id_int)
        if cached is not None:
            logger.info("✅ Cache hit for planet", extra={"planet_id": id_int})
            return cached

        # 2️⃣ Cache miss: query DB
        planet = PlanetRepository.get_by_id(id_int)
        if not planet:
            logger.warning("⚠️ Planet not found", extra={"planet_id": id_int})
            raise BaseAppException(
                message=f"Planet with ID {id_int} not found.",
                status_code=404,
                payload={"planet_id": id_int},
            )

        serialized = {
            "id": planet.id,
            "name": planet.name,
            "population": planet.population,
            "climates": planet.climates,
            "terrains": planet.terrains,
        }

        # 3️⃣ Cache the retrieved planet
        CacheManager.set_planet_in_cache(id_int, serialized)
        logger.info("✅ Planet cached", extra={"planet_id": id_int})
        return serialized

    @staticmethod
    def update_planet(planet_id: int, data: dict):
        """🛠️ Update a planet by ID, invalidate caches, and queue event."""
        id_int = int(planet_id)
        logger.info(
            "🛠️ Updating planet",
            extra={"planet_id": id_int, "data": data},
        )
        planet = PlanetRepository.get_by_id(id_int)
        if not planet:
            logger.warning(
                "⚠️ Planet not found for update",
                extra={"planet_id": id_int},
            )
            raise BaseAppException(
                message=f"Planet with ID {id_int} not found.",
                status_code=404,
                payload={"planet_id": id_int},
            )

        updated = PlanetRepository.update(planet, data)

        # Invalidate per-item and full-list caches
        CacheManager.invalidate_planet_cache(id_int)
        CacheManager.invalidate_all_planets_cache()

        # Queue update event via Celery
        publish_planet_event_task.delay(
            "updated",
            {
                "id": updated.id,
                "name": updated.name,
                "population": updated.population,
                "climates": updated.climates,
                "terrains": updated.terrains,
            },
        )
        logger.info(
            "✅ Planet updated (queued event)",
            extra={"planet_id": updated.id},
        )

        return {
            "id": updated.id,
            "name": updated.name,
            "population": updated.population,
            "climates": updated.climates,
            "terrains": updated.terrains,
        }

    @staticmethod
    def delete_planet(planet_id: int):
        """🗑️ Delete a planet by ID, invalidate caches, and queue event."""
        id_int = int(planet_id)
        logger.info("🗑️ Deleting planet", extra={"planet_id": id_int})
        planet = PlanetRepository.get_by_id(id_int)
        if not planet:
            logger.warning(
                "⚠️ Planet not found for deletion",
                extra={"planet_id": id_int},
            )
            raise BaseAppException(
                message=f"Planet with ID {id_int} not found.",
                status_code=404,
                payload={"planet_id": id_int},
            )

        PlanetRepository.delete(planet)

        # Invalidate caches
        CacheManager.invalidate_planet_cache(id_int)
        CacheManager.invalidate_all_planets_cache()

        # Queue deletion event via Celery
        publish_planet_event_task.delay("deleted", {"id": id_int})
        logger.info(
            "✅ Planet deleted (queued event)",
            extra={"planet_id": id_int},
        )

        return {
            "status": "success",
            "message": f"Planet {id_int} deleted.",
        }
