# 🌐 urls.py - Main URL configuration for the Django project

from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path, re_path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularJSONAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
    SpectacularYAMLAPIView,
)

urlpatterns = [
    # 📊 Prometheus metrics
    path("", include("django_prometheus.urls")),
    # 🛠️ Admin interface
    path("admin/", admin.site.urls),
    # 🚀 API endpoints
    path("api/", include("planets.urls")),
    path("api/analytics/", include("analytics.urls")),
    # 📄 OpenAPI schema endpoints (YAML, JSON, with/without trailing slash)
    re_path(r"^api/schema/?$", SpectacularAPIView.as_view(), name="schema"),
    re_path(
        r"^api/schema\.json/?$",
        SpectacularJSONAPIView.as_view(),
        name="schema-json",
    ),
    re_path(
        r"^api/schema\.yaml/?$",
        SpectacularYAMLAPIView.as_view(),
        name="schema-yaml",
    ),
    # 🖥️ Swagger UI (interactive API documentation)
    path(
        "api/docs/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/docs/swagger",
        SpectacularSwaggerView.as_view(url_name="schema"),
    ),
    # 📘 ReDoc UI (alternative API documentation)
    path(
        "api/docs/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    path(
        "api/docs/redoc",
        SpectacularRedocView.as_view(url_name="schema"),
    ),
]


# ───────────────────────────────────────────────────────────────────────────────
# JSON 404 handler for REST API
# ───────────────────────────────────────────────────────────────────────────────
def rest_not_found(request, exception):
    return JsonResponse({"detail": "Not Found"}, status=404)


handler404 = rest_not_found
