# 🪐 test_planet_repository.py - Tests for PlanetRepository using stubs

from repositories.planet_repository import PlanetRepository


class _DummyDoesNotExist(Exception):
    """Stub exception replicating Planet.DoesNotExist for tests."""


class DummyQuerySet(list):
    """Stub QuerySet with .count() support like Django QuerySet."""

    def count(self):
        return len(self)


class DummyManager:
    """Stub manager replacing Planet.objects for isolated tests."""

    def __init__(self, instance):
        self._instance = instance

    def get(self, id):
        if id == self._instance.id:
            return self._instance
        raise _DummyDoesNotExist

    def all(self):
        return DummyQuerySet([self._instance])

    def create(self, **data):
        # Return a "persisted" dummy planet with fixed ID
        return DummyPlanet(id=42, **data)


class DummyPlanet:
    """Stub model for isolated testing of the repository."""

    DoesNotExist = _DummyDoesNotExist

    def __init__(self, id, name, population=0, climates=None, terrains=None):
        self.id = id
        self.name = name
        self.population = population
        self.climates = climates or []
        self.terrains = terrains or []

    def save(self):
        """Stub save method."""
        pass

    def delete(self):
        """Stub delete method."""
        pass


# -------------------------------------------------------------------
# ✅ TEST: get_by_id - found
# -------------------------------------------------------------------


def test_get_by_id_found(mocker):
    """Should return the planet if it exists."""
    dummy = DummyPlanet(id=1, name="Naboo", population=4500000000)
    mocker.patch("repositories.planet_repository.Planet", DummyPlanet)
    DummyPlanet.objects = DummyManager(dummy)

    assert PlanetRepository.get_by_id(1) is dummy


# -------------------------------------------------------------------
# ✅ TEST: get_by_id - not found
# -------------------------------------------------------------------


def test_get_by_id_not_found(mocker):
    """Should return None if the planet is not found."""
    dummy = DummyPlanet(id=1, name="Naboo")
    mocker.patch("repositories.planet_repository.Planet", DummyPlanet)
    DummyPlanet.objects = DummyManager(dummy)

    assert PlanetRepository.get_by_id(999) is None


# -------------------------------------------------------------------
# ✅ TEST: list_all
# -------------------------------------------------------------------


def test_list_all(mocker):
    """Should list all planets from the repository."""
    dummy = DummyPlanet(id=7, name="Endor")
    mocker.patch("repositories.planet_repository.Planet", DummyPlanet)
    DummyPlanet.objects = DummyManager(dummy)

    planets = PlanetRepository.list_all()
    assert planets == [dummy]
    assert planets.count() == 1


# -------------------------------------------------------------------
# ✅ TEST: create
# -------------------------------------------------------------------


def test_create(mocker):
    """Should create and return a new planet using the repository."""
    mocker.patch("repositories.planet_repository.Planet", DummyPlanet)

    data = {
        "name": "Kamino",
        "population": 1_000_000,
        "climates": ["rainy"],
        "terrains": ["ocean"],
    }

    DummyPlanet.objects = DummyManager(DummyPlanet(id=0, name="stub"))

    created = PlanetRepository.create(data)

    assert created.id == 42
    for k, v in data.items():
        assert getattr(created, k) == v
