# 🪐 views.py - DRF ViewSet for Planet endpoints with OpenAPI documentation

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status, viewsets
from rest_framework.response import Response

from services.planet_service import PlanetService
from utils.exceptions import BaseAppException
from utils.rest_util import error_response, success_response

from .serializers import PlanetSerializer


class PlanetViewSet(viewsets.GenericViewSet):
    """
    DRF ViewSet for managing Planet resources via CRUD operations,
    using a service layer for clean business logic separation.
    """

    serializer_class = PlanetSerializer
    lookup_field = "planet_id"

    @extend_schema(summary="List all planets")
    def list(self, request):
        """Handles GET /api/planets/ to list all planets."""
        try:
            planets = PlanetService.list_all_planets()
            return success_response(data=planets)
        except BaseAppException as exc:
            return error_response(exc.message, exc.payload, exc.status_code)

    @extend_schema(
        summary="Create a new planet",
        request=PlanetSerializer,
        responses={201: PlanetSerializer},
    )
    def create(self, request):
        """Handles POST /api/planets/ to create a new planet."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        created = PlanetService.create_planet(serializer.validated_data)
        return success_response(
            data=created,
            message="Planet created",
            status_code=status.HTTP_201_CREATED,
        )

    @extend_schema(
        summary="Retrieve a planet by ID",
        parameters=[
            OpenApiParameter(
                name="planet_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="The ID of the planet to retrieve",
            )
        ],
        responses={200: PlanetSerializer},
    )
    def retrieve(self, request, planet_id=None):
        """Handles GET /api/planets/{planet_id}/ to retrieve a planet."""
        try:
            planet = PlanetService.get_planet_by_id(planet_id)
            return success_response(data=planet)
        except BaseAppException as exc:
            return error_response(exc.message, exc.payload, exc.status_code)

    @extend_schema(
        summary="Fully update a planet",
        parameters=[
            OpenApiParameter(
                name="planet_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="The ID of the planet to update",
            )
        ],
        request=PlanetSerializer,
        responses={200: PlanetSerializer},
    )
    def update(self, request, planet_id=None):
        """Handles PUT /api/planets/{planet_id}/ for full updates."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated = PlanetService.update_planet(planet_id, serializer.validated_data)
        return success_response(data=updated, message="Planet updated")

    @extend_schema(
        summary="Partially update a planet",
        parameters=[
            OpenApiParameter(
                name="planet_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="The ID of the planet to update",
            )
        ],
        request=PlanetSerializer,
        responses={200: PlanetSerializer},
    )
    def partial_update(self, request, planet_id=None):
        """Handles PATCH /api/planets/{planet_id}/ for partial updates."""
        serializer = self.get_serializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated = PlanetService.update_planet(planet_id, serializer.validated_data)
        return success_response(data=updated, message="Planet updated")

    @extend_schema(
        summary="Delete a planet",
        parameters=[
            OpenApiParameter(
                name="planet_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="The ID of the planet to delete",
            )
        ],
    )
    def destroy(self, request, planet_id=None):
        """Handles DELETE /api/planets/{planet_id}/ to delete a planet."""
        try:
            PlanetService.delete_planet(planet_id)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except BaseAppException as exc:
            return error_response(exc.message, exc.payload, exc.status_code)
