# 🪐 planet_repository.py - Repository for abstracting Planet data access

import logging

from planets.models import Planet

logger = logging.getLogger(__name__)


class PlanetRepository:
    """
    Repository for encapsulating Planet CRUD operations.
    """

    @staticmethod
    def get_by_id(planet_id: int):
        """
        Retrieve a planet by its ID or return None if not found.
        """
        logger.info("🔍 Retrieving Planet by ID", extra={"planet_id": planet_id})
        try:
            planet = Planet.objects.get(id=planet_id)
            logger.info(
                "✅ Planet retrieved successfully", extra={"planet_id": planet_id}
            )
            return planet
        except Planet.DoesNotExist:
            logger.warning("⚠️ Planet not found", extra={"planet_id": planet_id})
            return None

    @staticmethod
    def list_all():
        """
        Retrieve all planets in the database.
        """
        logger.info("🔍 Retrieving all Planets")
        planets = Planet.objects.all()
        logger.info("✅ Retrieved all Planets", extra={"planet_count": planets.count()})
        return planets

    @staticmethod
    def create(data: dict):
        """
        Create a new planet using provided data.
        """
        logger.info("🛠️ Creating Planet", extra={"data": data})
        planet = Planet.objects.create(
            name=data.get("name"),
            population=data.get("population"),
            climates=data.get("climates", []),
            terrains=data.get("terrains", []),
        )
        logger.info("✅ Planet created", extra={"planet_id": planet.id})
        return planet

    @staticmethod
    def update(planet, data: dict):
        """
        Update an existing planet with the provided data.
        """
        logger.info(
            "🛠️ Updating Planet",
            extra={"planet_id": planet.id, "data": data},
        )
        planet.name = data.get("name", planet.name)
        planet.population = data.get("population", planet.population)
        planet.climates = data.get("climates", planet.climates)
        planet.terrains = data.get("terrains", planet.terrains)
        planet.save()
        logger.info("✅ Planet updated", extra={"planet_id": planet.id})
        return planet

    @staticmethod
    def delete(planet):
        """
        Delete a planet from the database.
        """
        logger.info("🗑️ Deleting Planet", extra={"planet_id": planet.id})
        planet.delete()
        logger.info("✅ Planet deleted", extra={"planet_id": planet.id})
