# 🪐 test_tasks.py - Unit tests for Celery tasks in planets.tasks

from types import SimpleNamespace

from planets.tasks import fetch_and_store_planets, publish_planet_event_task

# -------------------------------------------------------------------
# 🛠️ Helpers
# -------------------------------------------------------------------


def _graphql_payload(planets):
    """Returns a mock GraphQL payload structure as returned by the API."""
    return {"data": {"allPlanets": {"planets": planets}}}


# -------------------------------------------------------------------
# ✅ Tests for fetch_and_store_planets
# -------------------------------------------------------------------


def test_fetch_and_store_planets_success(mocker):
    """
    Tests that:
    - API is called successfully.
    - Planet.objects.update_or_create is called for each planet.
    - Logs a success message.
    """
    planets_api = [
        {
            "name": "Naboo",
            "population": "4500000000",
            "terrains": ["grassy hills", "swamps"],
            "climates": ["temperate"],
        },
        {
            "name": "Dagobah",
            "population": "unknown",
            "terrains": ["swamp", "jungles"],
            "climates": ["murky"],
        },
    ]

    # Mock requests.post
    mocked_resp = mocker.Mock(
        status_code=200,
        json=lambda: _graphql_payload(planets_api),
    )
    mocked_resp.raise_for_status = mocker.Mock()
    mocker.patch("planets.tasks.requests.post", return_value=mocked_resp)

    # Mock breaker.call to return mocked_resp
    mocker.patch("planets.tasks.breaker.call", side_effect=lambda *a, **k: mocked_resp)

    # Mock Planet.objects.update_or_create
    mocked_uoc = mocker.patch("planets.tasks.Planet.objects.update_or_create")

    # Mock logger
    mocked_logger = mocker.patch("planets.tasks.logger")

    # Execute task
    fetch_and_store_planets.run()

    # Assertions
    mocked_resp.raise_for_status.assert_called_once()
    assert mocked_uoc.call_count == len(planets_api)
    mocked_uoc.assert_any_call(
        name="Naboo",
        defaults={
            "population": 4500000000,
            "terrains": ["grassy hills", "swamps"],
            "climates": ["temperate"],
        },
    )
    mocked_uoc.assert_any_call(
        name="Dagobah",
        defaults={
            "population": None,
            "terrains": ["swamp", "jungles"],
            "climates": ["murky"],
        },
    )
    mocked_logger.info.assert_called_with(
        "✅ fetch_and_store_planets completed successfully."
    )


def test_fetch_and_store_planets_circuit_open(mocker):
    """
    If the circuit breaker raises CircuitBreakerError,
    the task should not call update_or_create and should log the error.
    """
    from pybreaker import CircuitBreakerError

    mocker.patch(
        "planets.tasks.breaker.call",
        side_effect=CircuitBreakerError("open"),
    )
    mocked_uoc = mocker.patch("planets.tasks.Planet.objects.update_or_create")
    mocked_logger = mocker.patch("planets.tasks.logger")

    fetch_and_store_planets.run()

    mocked_uoc.assert_not_called()
    mocked_logger.error.assert_called()


# -------------------------------------------------------------------
# ✅ Tests for publish_planet_event_task
# -------------------------------------------------------------------


def test_publish_planet_event_task_invokes_publisher(mocker):
    """Test that publish_planet_event_task calls the Kafka publisher."""
    event_type = "created"
    data = {"id": 77, "name": "Endor"}

    mocked_publish = mocker.patch("planets.tasks.KafkaPublisher.publish_planet_event")

    publish_planet_event_task.run(event_type, data)

    mocked_publish.assert_called_once_with(event_type, data)
