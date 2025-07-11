# 🪐 test_planet_model.py - Unit tests for Planet model without Django runtime

"""
Unit tests for the Planet model without requiring Django:
simulates django.db.models using minimal stubs for isolated testing.
"""

import importlib
import sys
import types


def _install_django_model_stubs() -> None:
    """
    Inserts a fake `django.db.models` module into sys.modules with the
    minimal attributes expected by `planets.models`.
    """
    fake_models = types.ModuleType("django.db.models")

    # Fake fields: return a generic object
    _dummy_field = lambda *a, **kw: object()

    # Base class and required fields
    fake_models.Model = object
    fake_models.CharField = _dummy_field
    fake_models.IntegerField = _dummy_field
    fake_models.JSONField = _dummy_field
    fake_models.DateTimeField = _dummy_field

    # Insert intermediate modules
    sys.modules.setdefault("django", types.ModuleType("django"))
    sys.modules.setdefault("django.db", types.ModuleType("django.db"))
    sys.modules["django.db.models"] = fake_models


# -------------------------------------------------------------------
# ✅ TESTS
# -------------------------------------------------------------------


def test_planet_str():
    """
    Tests that Planet.__str__ correctly formats name and None population.
    """
    _install_django_model_stubs()
    Planet = importlib.import_module("planets.models").Planet

    p = Planet()
    p.name = "Dagobah"
    p.population = None

    assert str(p) == "Dagobah (Population: None)"


def test_planet_str_with_population():
    """
    Tests that Planet.__str__ correctly formats name with numeric population.
    """
    _install_django_model_stubs()
    Planet = importlib.import_module("planets.models").Planet

    p = Planet()
    p.name = "Alderaan"
    p.population = 2_000_000

    assert str(p) == "Alderaan (Population: 2000000)"
