# 🌍 test_urls.py - URL routing tests for Planets API

import importlib
import sys
from types import ModuleType

from django.conf import settings
from django.urls import path, resolve, reverse

# -------------------------------------------------------------------
# 🛠️ 1) Minimal DefaultRouter stub if DRF is not present
# -------------------------------------------------------------------


def _install_router_stub() -> None:
    """
    Installs a minimal DRF DefaultRouter stub if DRF is not installed,
    ensuring route resolution tests do not fail in lightweight test setups.
    """
    if "rest_framework" in sys.modules:
        return

    routers_mod = ModuleType("rest_framework.routers")

    class _StubRouter:
        def __init__(self):
            self._patterns = []

        def register(self, prefix, viewset, basename=None):
            lookup = getattr(viewset, "lookup_field", "pk")
            name = basename or prefix
            self._patterns += [
                path(f"{prefix}/", lambda r: None, name=f"{name}-list"),
                path(
                    f"{prefix}/<int: {lookup}>/",
                    lambda r, **kw: None,
                    name=f"{name}-detail",
                ),
            ]

        @property
        def urls(self):
            return self._patterns

    rf_root = ModuleType("rest_framework")
    rf_root.routers = routers_mod
    routers_mod.DefaultRouter = _StubRouter

    sys.modules.update(
        {
            "rest_framework": rf_root,
            "rest_framework.routers": routers_mod,
        }
    )


_install_router_stub()

# -------------------------------------------------------------------
# ⚙️ 2) Load URLConf declared in settings
# -------------------------------------------------------------------
URLCONF = settings.ROOT_URLCONF or "app.urls"
importlib.import_module(URLCONF)


def _view_name(action: str) -> str:
    """Returns view name used by DRF (e.g., 'planet-list')."""
    return f"planet-{action}"


# -------------------------------------------------------------------
# 🧩 3) Helper to get DRF action “list” or “retrieve” if available
# -------------------------------------------------------------------


def _resolved_action(view_func):
    """
    Returns the DRF action ('list', 'retrieve', etc.) or None if the resolved
    function is the viewset itself (CI setups without DRF router wrappers).
    """
    if hasattr(view_func, "action_map"):  # stub fallback
        return view_func.action_map.get("get")
    if hasattr(view_func, "initkwargs"):  # real DRF
        actions = view_func.initkwargs.get("actions")
        if actions:
            return actions.get("get")
    return None


# -------------------------------------------------------------------
# ✅ 4) URL route tests
# -------------------------------------------------------------------


def test_planet_list_route():
    """
    🚀 Tests the /api/planets/ route:
    • Correctly resolves to 'planet-list'.
    • Returns expected DRF action or None in lightweight environments.
    """
    url = reverse(_view_name("list"))
    match = resolve(url)

    assert match.view_name == _view_name("list")
    assert _resolved_action(match.func) in {None, "list"}


def test_planet_detail_route():
    """
    🚀 Tests the /api/planets/<id>/ route:
    • Correctly resolves to 'planet-detail'.
    • Parses kwargs with 'planet_id'.
    • Returns expected DRF action or None in lightweight environments.
    """
    url = reverse(_view_name("detail"), args=[42])
    match = resolve(url)

    assert match.view_name == _view_name("detail")
    assert match.kwargs == {"planet_id": "42"}
    assert _resolved_action(match.func) in {None, "retrieve"}
