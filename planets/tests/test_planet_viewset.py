# 🪐 test_planet_viewset.py - E2E/unit tests for PlanetViewSet behavior

import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory

from planets.views import PlanetViewSet

# -------------------------------------------------------------------
# 🛠️ Helpers
# -------------------------------------------------------------------

factory = APIRequestFactory()


def _as_view(method: str):
    """
    Returns the callable view for the desired HTTP verb on PlanetViewSet.
    """
    http_map = {
        "list": {"get": "list"},
        "retrieve": {"get": "retrieve"},
        "create": {"post": "create"},
        "update": {"put": "update"},
        "partial_update": {"patch": "partial_update"},
        "destroy": {"delete": "destroy"},
    }
    return PlanetViewSet.as_view(http_map[method])


# -------------------------------------------------------------------
# ✅ 1) List Planets
# -------------------------------------------------------------------


def test_list_planets_success(mocker):
    """Test listing planets returns 200 with expected data."""
    planets_data = [{"id": 1, "name": "Naboo"}]

    mocker.patch(
        "planets.views.PlanetService.list_all_planets",
        return_value=planets_data,
    )

    request = factory.get("/planets/")
    response = _as_view("list")(request)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"status": "success", "data": planets_data}


# -------------------------------------------------------------------
# ✅ 2) Retrieve Planet - Success
# -------------------------------------------------------------------


def test_retrieve_planet_success(mocker):
    """Test retrieving a planet returns 200 with expected data."""
    planet = {"id": 1, "name": "Naboo"}

    mocker.patch(
        "planets.views.PlanetService.get_planet_by_id",
        return_value=planet,
    )

    request = factory.get("/planets/1/")
    response = _as_view("retrieve")(request, planet_id=1)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["data"] == planet


# -------------------------------------------------------------------
# ✅ 3) Retrieve Planet - Not Found
# -------------------------------------------------------------------


def test_retrieve_planet_not_found(mocker):
    """Test retrieving a non-existent planet returns a 404 error."""
    from utils.exceptions import BaseAppException

    exc = BaseAppException("not-found", status_code=404, payload={"planet_id": 1})
    mocker.patch(
        "planets.views.PlanetService.get_planet_by_id",
        side_effect=exc,
    )

    request = factory.get("/planets/1/")
    resp = _as_view("retrieve")(request, planet_id=1)

    assert resp.status_code == 404
    assert resp.data == {
        "status": "error",
        "message": "not-found",
        "errors": {"planet_id": 1},
    }


# -------------------------------------------------------------------
# ✅ 4) Create Planet - Success
# -------------------------------------------------------------------


def test_create_planet_success(mocker):
    """Test creating a planet returns 201 with created data."""
    created = {
        "id": 42,
        "name": "Kamino",
        "population": 1_000_000,
        "climates": ["rainy"],
        "terrains": ["ocean"],
    }

    mocker.patch(
        "planets.views.PlanetService.create_planet",
        return_value=created,
    )

    payload = created | {"id": None}

    class DummySer:
        def __init__(self, *_, **kw):
            self.validated_data = kw.get("data") or {}

        def is_valid(self, **_):
            return True

    mocker.patch("planets.views.PlanetSerializer", DummySer)
    mocker.patch.object(PlanetViewSet, "serializer_class", DummySer, autospec=False)

    req = factory.post("/planets/", payload, format="json")
    resp = _as_view("create")(req)

    assert resp.status_code == status.HTTP_201_CREATED
    assert resp.data["data"] == created


# -------------------------------------------------------------------
# ✅ 5) Update Planet - Not Found
# -------------------------------------------------------------------


def test_update_planet_not_found(mocker):
    """Test updating a non-existent planet raises BaseAppException."""
    from utils.exceptions import BaseAppException

    exc = BaseAppException("nf-update", status_code=404, payload={"planet_id": 99})
    mocker.patch(
        "planets.views.PlanetService.update_planet",
        side_effect=exc,
    )

    class DummySer:
        def __init__(self, *_, **kw):
            self.validated_data = kw.get("data") or {}

        def is_valid(self, **_):
            return True

    mocker.patch("planets.views.PlanetSerializer", DummySer)
    mocker.patch.object(PlanetViewSet, "serializer_class", DummySer, autospec=False)

    request = factory.put("/planets/99/", {"name": "X"}, format="json")

    with pytest.raises(BaseAppException):
        _as_view("update")(request, planet_id=99)


# -------------------------------------------------------------------
# ✅ 6) Update Planet - Success
# -------------------------------------------------------------------


def test_update_planet_success(mocker):
    """Test updating a planet returns 200 with updated data."""
    updated = {
        "id": 7,
        "name": "Endor",
        "population": 10,
        "climates": [],
        "terrains": [],
    }
    mocker.patch(
        "planets.views.PlanetService.update_planet",
        return_value=updated,
    )

    class DummySer:
        def __init__(self, *_, **kw):
            self.validated_data = kw.get("data") or {}

        def is_valid(self, **_):
            return True

    mocker.patch("planets.views.PlanetSerializer", DummySer)
    mocker.patch.object(PlanetViewSet, "serializer_class", DummySer, autospec=False)

    req = factory.put("/planets/7/", {"name": "Endor"}, format="json")
    resp = _as_view("update")(req, planet_id=7)

    assert resp.status_code == 200
    assert resp.data["data"]["name"] == "Endor"


# -------------------------------------------------------------------
# ✅ 7) Delete Planet - Not Found
# -------------------------------------------------------------------


def test_destroy_planet_not_found(mocker):
    """Test deleting a non-existent planet returns a 404 error."""
    from utils.exceptions import BaseAppException

    exc = BaseAppException("nf-delete", status_code=404, payload={"planet_id": 123})
    mocker.patch(
        "planets.views.PlanetService.delete_planet",
        side_effect=exc,
    )

    request = factory.delete("/planets/123/")
    resp = _as_view("destroy")(request, planet_id=123)

    assert resp.status_code == 404
    assert resp.data == {
        "status": "error",
        "message": "nf-delete",
        "errors": {"planet_id": 123},
    }
