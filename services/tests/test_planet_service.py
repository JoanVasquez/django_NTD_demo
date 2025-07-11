# 🚀 test_planet_service.py - Unit tests for PlanetService

import pytest

from services.planet_service import PlanetService
from utils.exceptions import BaseAppException

# -------------------------------------------------------------------
# 🧩 Helpers / Dummies
# -------------------------------------------------------------------


class DummyPlanet:
    """Minimal dummy planet for repository-independent tests."""

    def __init__(
        self, _id=1, name="Naboo", population=10, climates=None, terrains=None
    ):
        self.id = _id
        self.name = name
        self.population = population
        self.climates = climates or []
        self.terrains = terrains or []


# -------------------------------------------------------------------
# ✅ list_all_planets
# -------------------------------------------------------------------


def test_list_all_cache_hit(mocker):
    """Should return cached planets and avoid DB call."""
    cached = [{"id": 1, "name": "Naboo"}]

    mocker.patch(
        "services.planet_service.CacheManager.get_all_planets_from_cache",
        return_value=cached,
    )
    repo_list = mocker.patch("services.planet_service.PlanetRepository.list_all")

    result = PlanetService.list_all_planets()

    assert result == cached
    repo_list.assert_not_called()


def test_list_all_cache_miss(mocker):
    """Should fetch from DB and store in cache on cache miss."""
    mocker.patch(
        "services.planet_service.CacheManager.get_all_planets_from_cache",
        return_value=None,
    )
    dummy = DummyPlanet()
    mocker.patch(
        "services.planet_service.PlanetRepository.list_all", return_value=[dummy]
    )
    set_cache = mocker.patch(
        "services.planet_service.CacheManager.set_all_planets_in_cache"
    )

    result = PlanetService.list_all_planets()

    assert result == [
        {
            "id": dummy.id,
            "name": dummy.name,
            "population": dummy.population,
            "climates": dummy.climates,
            "terrains": dummy.terrains,
        }
    ]
    set_cache.assert_called_once()


# -------------------------------------------------------------------
# ✅ create_planet
# -------------------------------------------------------------------


def test_create_planet_ok(mocker):
    """Should create a planet and publish an event."""
    data_in = {"name": "Kamino", "population": 10, "climates": [], "terrains": []}
    dummy = DummyPlanet(_id=7, **data_in)

    mocker.patch("services.planet_service.PlanetRepository.create", return_value=dummy)
    inv_cache = mocker.patch(
        "services.planet_service.CacheManager.invalidate_all_planets_cache"
    )
    task = mocker.patch("services.planet_service.publish_planet_event_task")

    result = PlanetService.create_planet(data_in)

    assert result["id"] == 7
    assert result["name"] == "Kamino"
    inv_cache.assert_called_once()
    task.delay.assert_called_once_with("created", result)


# -------------------------------------------------------------------
# ✅ get_planet_by_id
# -------------------------------------------------------------------


def test_get_by_id_cache_hit(mocker):
    """Should return cached planet and skip DB."""
    cached = {"id": 1, "name": "Endor"}
    mocker.patch(
        "services.planet_service.CacheManager.get_planet_from_cache",
        return_value=cached,
    )
    repo_get = mocker.patch("services.planet_service.PlanetRepository.get_by_id")

    assert PlanetService.get_planet_by_id(1) == cached
    repo_get.assert_not_called()


def test_get_by_id_not_found(mocker):
    """Should raise BaseAppException if planet not found."""
    mocker.patch(
        "services.planet_service.CacheManager.get_planet_from_cache",
        return_value=None,
    )
    mocker.patch(
        "services.planet_service.PlanetRepository.get_by_id",
        return_value=None,
    )

    with pytest.raises(BaseAppException) as exc:
        PlanetService.get_planet_by_id(99)

    assert exc.value.status_code == 404


def test_get_by_id_cache_miss_ok(mocker):
    """Should fetch planet from DB, store in cache, and return it."""
    mocker.patch(
        "services.planet_service.CacheManager.get_planet_from_cache",
        return_value=None,
    )
    dummy = DummyPlanet()
    mocker.patch(
        "services.planet_service.PlanetRepository.get_by_id",
        return_value=dummy,
    )
    set_cache = mocker.patch("services.planet_service.CacheManager.set_planet_in_cache")

    result = PlanetService.get_planet_by_id(1)

    assert result["id"] == 1
    assert result["name"] == "Naboo"
    set_cache.assert_called_once_with(1, result)


# -------------------------------------------------------------------
# ✅ update_planet
# -------------------------------------------------------------------


def test_update_planet_ok(mocker):
    """Should update a planet, invalidate cache, and publish event."""
    original = DummyPlanet()
    updated = DummyPlanet(name="Naboo-II")

    mocker.patch(
        "services.planet_service.PlanetRepository.get_by_id",
        return_value=original,
    )
    mocker.patch(
        "services.planet_service.PlanetRepository.update",
        return_value=updated,
    )
    inv_p = mocker.patch("services.planet_service.CacheManager.invalidate_planet_cache")
    inv_all = mocker.patch(
        "services.planet_service.CacheManager.invalidate_all_planets_cache"
    )
    task = mocker.patch("services.planet_service.publish_planet_event_task")

    res = PlanetService.update_planet(1, {"name": "Naboo-II"})

    assert res["name"] == "Naboo-II"
    inv_p.assert_called_once_with(1)
    inv_all.assert_called_once()
    task.delay.assert_called_once()


def test_update_planet_not_found(mocker):
    """Should raise BaseAppException if updating a non-existent planet."""
    mocker.patch(
        "services.planet_service.PlanetRepository.get_by_id",
        return_value=None,
    )

    with pytest.raises(BaseAppException):
        PlanetService.update_planet(9, {"name": "X"})


# -------------------------------------------------------------------
# ✅ delete_planet
# -------------------------------------------------------------------


def test_delete_planet_ok(mocker):
    """Should delete a planet, invalidate cache, and publish event."""
    dummy = DummyPlanet()

    mocker.patch(
        "services.planet_service.PlanetRepository.get_by_id",
        return_value=dummy,
    )
    delete_repo = mocker.patch("services.planet_service.PlanetRepository.delete")
    inv_p = mocker.patch("services.planet_service.CacheManager.invalidate_planet_cache")
    inv_all = mocker.patch(
        "services.planet_service.CacheManager.invalidate_all_planets_cache"
    )
    task = mocker.patch("services.planet_service.publish_planet_event_task")

    res = PlanetService.delete_planet(1)

    delete_repo.assert_called_once_with(dummy)
    inv_p.assert_called_once_with(1)
    inv_all.assert_called_once()
    task.delay.assert_called_once_with("deleted", {"id": 1})
    assert res["status"] == "success"


def test_delete_planet_not_found(mocker):
    """Should raise BaseAppException if deleting a non-existent planet."""
    mocker.patch(
        "services.planet_service.PlanetRepository.get_by_id",
        return_value=None,
    )

    with pytest.raises(BaseAppException):
        PlanetService.delete_planet(123)
