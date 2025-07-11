# 🌍 test_e2e_planets_api.py - E2E tests for Planets API

import json

import pytest
from django.test import Client
from django.urls import reverse

from planets.models import Planet

# -------------------------------------------------------------------
# 🧪 1) Fixtures and monkey-patches for E2E test environment
# -------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _patch_response_and_celery(mocker):
    """
    Auto-applied fixture:
    • Patch rest_framework.response.Response to return Django JsonResponse
      so the Django test client can handle E2E payloads.
    • Disable Celery .delay to prevent real task execution during tests.
    """
    import rest_framework.response as rf_resp_mod
    from django.http import JsonResponse

    class _PatchedResponse(JsonResponse):
        def __init__(self, data, status=200):
            # safe=False allows lists in payload
            super().__init__(data, status=status, safe=False)

    rf_resp_mod.Response = _PatchedResponse

    mocker.patch(
        "services.planet_service.publish_planet_event_task.delay",
        return_value=None,
    )


@pytest.fixture
def client():
    """🚀 Provides Django test client for API calls."""
    return Client()


# -------------------------------------------------------------------
# 🛠️ 2) Helpers
# -------------------------------------------------------------------


def _planet_payload(name="Dagobah", population=1000):
    """Generates a representative JSON payload for a planet."""
    return {
        "name": name,
        "population": population,
        "terrains": ["swamp"],
        "climates": ["humid"],
    }


# -------------------------------------------------------------------
# ✅ 3) E2E Tests
# -------------------------------------------------------------------


@pytest.mark.django_db
def test_create_get_list_flow(client):
    """
    Validates:
    • POST  /api/planets/          → 201 + returned body
    • GET   /api/planets/<id>/     → 200 + same body
    • GET   /api/planets/          → 200 + list including the planet
    """
    list_url = reverse("planet-list")
    payload = _planet_payload("Coruscant", 1_000_000_000)

    # 🚀 CREATE
    resp = client.post(
        list_url,
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert resp.status_code == 201
    data = resp.json()["data"]
    planet_id = data["id"]
    assert data["name"] == payload["name"]

    # 👁️ RETRIEVE
    detail_url = reverse("planet-detail", args=[planet_id])
    resp = client.get(detail_url)
    assert resp.status_code == 200
    assert resp.json()["data"]["name"] == payload["name"]

    # 📜 LIST
    resp = client.get(list_url)
    lst = resp.json()["data"]
    assert len(lst) == 1
    assert lst[0]["id"] == planet_id


@pytest.mark.django_db
def test_delete_flow(client):
    """
    Validates:
    • Create a planet directly in the DB.
    • DELETE /api/planets/<id>/    → 204
    • GET    /api/planets/<id>/    → 404
    """
    planet = Planet.objects.create(
        name="Alderaan",
        population=2_000_000,
        terrains=["grasslands"],
        climates=["temperate"],
    )
    detail_url = reverse("planet-detail", args=[planet.id])

    # 🗑️ DELETE
    resp = client.delete(detail_url)
    assert resp.status_code == 204

    # 🕵️ VERIFY 404
    resp = client.get(detail_url)
    assert resp.status_code == 404
    body = resp.json()
    assert body["status"] == "error"
    assert body["errors"]["planet_id"] == planet.id
