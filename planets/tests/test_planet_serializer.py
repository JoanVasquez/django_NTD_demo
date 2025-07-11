# 🪐 test_planet_serializer.py - Unit test for PlanetSerializer without DRF

"""
Unit test for PlanetSerializer without requiring DRF or Django models.
Creates stubs for `rest_framework.serializers` and `planets.models`,
then locates and tests the serializer definition in:
    - serializers
    - serializers.planet_serializer
    - planets.serializers
"""

import sys
import types
from importlib import import_module

import pytest


def _install_stubs() -> None:
    """Install stubs for DRF serializers and Planet model if not loaded."""
    rf_pkg = types.ModuleType("rest_framework")
    rf_ser = types.ModuleType("rest_framework.serializers")

    class _Base:
        pass

    rf_ser.Serializer = _Base
    rf_ser.ModelSerializer = _Base
    rf_pkg.serializers = rf_ser
    sys.modules["rest_framework"] = rf_pkg
    sys.modules["rest_framework.serializers"] = rf_ser

    if "planets" not in sys.modules:
        planets_pkg = types.ModuleType("planets")
        planets_models = types.ModuleType("planets.models")

        class Planet:
            pass

        planets_models.Planet = Planet
        planets_pkg.models = planets_models
        sys.modules["planets"] = planets_pkg
        sys.modules["planets.models"] = planets_models


_CANDIDATES = [
    "serializers",
    "serializers.planet_serializer",
    "planets.serializers",
]


def _import_serializer_module():
    """Try importing the module containing PlanetSerializer."""
    for mod_name in _CANDIDATES:
        try:
            module = import_module(mod_name)
            if hasattr(module, "PlanetSerializer"):
                return module
        except ModuleNotFoundError:
            continue
    pytest.fail(
        "Could not find a module containing PlanetSerializer " f"in: {_CANDIDATES}"
    )


_EXPECTED_FIELDS = [
    "id",
    "name",
    "population",
    "terrains",
    "climates",
    "created_at",
    "updated_at",
]
_READ_ONLY_FIELDS = ["id", "created_at", "updated_at"]


def test_planet_serializer_meta_fields():
    """Verify PlanetSerializer.Meta defines fields and read-only fields correctly."""
    _install_stubs()
    ser_mod = _import_serializer_module()
    PlanetSerializer = ser_mod.PlanetSerializer

    assert list(PlanetSerializer.Meta.fields) == _EXPECTED_FIELDS
    assert list(PlanetSerializer.Meta.read_only_fields) == _READ_ONLY_FIELDS
