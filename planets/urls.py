# planets/urls.py

from django.urls import re_path

from planets.views import PlanetViewSet

# Map list & create:
planets_list = PlanetViewSet.as_view(
    {
        "get": "list",
        "post": "create",
    }
)

# Map retrieve, update, partial_update & destroy:
planets_detail = PlanetViewSet.as_view(
    {
        "get": "retrieve",
        "put": "update",
        "patch": "partial_update",
        "delete": "destroy",
    }
)

urlpatterns = [
    # GET /api/planets  or /api/planets/
    re_path(r"^planets/?$", planets_list, name="planet-list"),
    # GET /api/planets/25  or /api/planets/25/
    re_path(r"^planets/(?P<planet_id>\d+)/?$", planets_detail, name="planet-detail"),
]
