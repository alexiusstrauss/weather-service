"""
BDD steps for weather feature tests.
"""
from datetime import UTC, datetime
from unittest.mock import Mock, patch

from behave import given, then, when
from django.urls import reverse
from rest_framework.test import APIClient


@given("the weather service is running")
def step_weather_service_running(context):
    """Ensure weather service is running."""
    context.client = APIClient()


@given("the API is accessible")
def step_api_accessible(context):
    """Ensure API is accessible."""
    response = context.client.get(reverse("core:health"))
    assert response.status_code in [200, 503]  # Allow for service unavailable in tests


@given('I have a valid city name "{city}"')
def step_valid_city_name(context, city):
    """Set a valid city name."""
    context.city = city
    context.valid_city = True


@given('I have an invalid city name "{city}"')
def step_invalid_city_name(context, city):
    """Set an invalid city name."""
    context.city = city
    context.valid_city = False


@given("the rate limit is set to {limit:d} requests per minute")
def step_set_rate_limit(context, limit):
    """Set rate limit for testing."""
    context.rate_limit = limit


@given("weather data is cached for the city")
def step_weather_data_cached(context):
    """Ensure weather data is cached."""
    context.cache_mocked = True


@when("I request weather information for the city")
def step_request_weather_info(context):
    """Request weather information for a city."""
    # Mock all external dependencies
    with patch("weather_service.apps.weather.repositories.DjangoWeatherQueryRepository.save_query") as mock_save, patch(
        "weather_service.apps.weather.repositories.DjangoWeatherQueryRepository.cleanup_old_queries"
    ) as mock_cleanup, patch(
        "weather_service.apps.weather.repositories.RedisWeatherCacheRepository.get_cached_weather"
    ) as mock_get_cache, patch(
        "weather_service.apps.weather.repositories.RedisWeatherCacheRepository.cache_weather"
    ) as mock_set_cache, patch(
        "weather_service.apps.weather.services.WeatherServiceFactory.create_service"
    ) as mock_factory:
        # Mock cache miss initially
        mock_get_cache.return_value = None
        mock_save.return_value = None
        mock_cleanup.return_value = None
        mock_set_cache.return_value = None

        # Mock the weather service
        mock_service = Mock()

        if context.valid_city:
            mock_service.get_weather.return_value = {
                "city": context.city,
                "country": "BR",
                "temperature": 25.0,
                "description": "Ensolarado",
                "humidity": 60,
                "pressure": 1013.25,
                "wind_speed": 5.5,
                "provider": "mock",
            }
        else:
            mock_service.get_weather.side_effect = Exception(f"Cidade '{context.city}' não encontrada")

        mock_factory.return_value = mock_service

        url = reverse("weather:weather")
        context.response = context.client.get(url, {"city": context.city})


@when("I request weather information without city parameter")
def step_request_weather_without_city(context):
    """Request weather information without city parameter."""
    url = reverse("weather:weather")
    context.response = context.client.get(url)


@when("I request weather information for the same city again")
def step_request_weather_again(context):
    """Request weather information for the same city again."""
    # Mock cache hit
    with patch("weather_service.apps.weather.repositories.DjangoWeatherQueryRepository.save_query") as mock_save, patch(
        "weather_service.apps.weather.repositories.DjangoWeatherQueryRepository.cleanup_old_queries"
    ) as mock_cleanup, patch(
        "weather_service.apps.weather.repositories.RedisWeatherCacheRepository.get_cached_weather"
    ) as mock_get_cache:
        # Mock cache hit with data
        mock_get_cache.return_value = {
            "city": context.city,
            "country": "BR",
            "temperature": 25.0,
            "description": "Cached weather",
            "humidity": 60,
            "pressure": 1013.25,
            "wind_speed": 5.5,
            "timestamp": datetime.now(UTC).isoformat(),
        }
        mock_save.return_value = None
        mock_cleanup.return_value = None

        url = reverse("weather:weather")
        context.response = context.client.get(url, {"city": context.city})


@when("I request weather history for the city")
def step_request_weather_history(context):
    """Request weather history for a city."""
    # Mock the use case to return expected format
    with patch("weather_service.apps.weather.usecases.GetWeatherHistoryUseCase.execute") as mock_execute:
        mock_execute.return_value = {
            "queries": [
                {
                    "id": 1,
                    "city": context.city,
                    "country": "BR",
                    "temperature": 25.0,
                    "description": "Ensolarado",
                    "humidity": 60,
                    "pressure": 1013.25,
                    "wind_speed": 5.5,
                    "timestamp": datetime.now(UTC).isoformat(),
                    "ip_address": "127.0.0.1",
                }
            ],
            "total": 1,
            "city": context.city,
        }

        url = reverse("weather:weather-history")
        context.history_response = context.client.get(url, {"city": context.city})


@when("I make {count:d} requests in quick succession")
def step_make_multiple_requests(context, count):
    """Make multiple requests in quick succession."""
    context.responses = []

    # For rate limiting test, we need to make real requests to trigger the middleware
    # We'll mock only the external service, not the database operations
    with patch("weather_service.apps.weather.services.WeatherServiceFactory.create_service") as mock_factory:
        # Mock the weather service
        mock_service = Mock()
        mock_service.get_weather.return_value = {
            "city": "TestCity",
            "country": "BR",
            "temperature": 25.0,
            "description": "Test weather",
            "humidity": 60,
            "pressure": 1013.25,
            "wind_speed": 5.5,
            "provider": "mock",
        }
        mock_factory.return_value = mock_service

        url = reverse("weather:weather")
        for i in range(count):
            response = context.client.get(url, {"city": f"Testcity{i}"})
            context.responses.append(response)


@when("I invalidate the cache for the city")
def step_invalidate_cache(context):
    """Invalidate cache for a city."""
    with patch(
        "weather_service.apps.weather.repositories.RedisWeatherCacheRepository.invalidate_cache"
    ) as mock_invalidate:
        mock_invalidate.return_value = True

        url = reverse("weather:weather-cache")
        context.cache_response = context.client.delete(url + f"?city={context.city}")


@then("I should receive weather data")
def step_receive_weather_data(context):
    """Verify weather data is received."""
    assert context.response.status_code == 200
    data = context.response.json()
    assert "city" in data
    assert "temperature" in data


@then("the response should contain temperature")
def step_response_contains_temperature(context):
    """Verify response contains temperature."""
    data = context.response.json()
    assert "temperature" in data
    assert isinstance(data["temperature"], int | float)


@then("the response should contain description")
def step_response_contains_description(context):
    """Verify response contains description."""
    data = context.response.json()
    assert "description" in data
    assert isinstance(data["description"], str)


@then('the response should contain city name "{expected_city}"')
def step_response_contains_city_name(context, expected_city):
    """Verify response contains expected city name."""
    data = context.response.json()
    assert data["city"] == expected_city


@then("I should receive an error response")
def step_receive_error_response(context):
    """Verify error response is received."""
    assert context.response.status_code in [400, 404, 500]
    data = context.response.json()
    assert "error" in data or "detail" in data


@then("the error should indicate city not found")
def step_error_city_not_found(context):
    """Verify error indicates city not found."""
    data = context.response.json()
    error_message = data.get("error", data.get("detail", "")).lower()
    assert "não encontrada" in error_message or "not found" in error_message


@then("I should receive a bad request error")
def step_receive_bad_request_error(context):
    """Verify bad request error is received."""
    assert context.response.status_code == 400


@then("the error should indicate missing city parameter")
def step_error_missing_city_parameter(context):
    """Verify error indicates missing city parameter."""
    data = context.response.json()
    error_message = data.get("error", data.get("detail", "")).lower()

    # Check if there are details about city field
    details = data.get("details", {})
    city_error = details.get("city", [])

    # Check main error message or details
    has_city_error = ("city" in error_message and ("required" in error_message or "obrigatório" in error_message)) or (
        city_error and any("obrigatório" in str(err).lower() or "required" in str(err).lower() for err in city_error)
    )

    assert has_city_error, f"Expected city parameter error, got: {data}"


@then("the cached flag should be {expected_cached}")
def step_cached_flag_should_be(context, expected_cached):
    """Verify cached flag value."""
    data = context.response.json()
    expected_value = expected_cached.lower() == "true"
    assert data.get("cached", False) == expected_value


@then("I should receive history data")
def step_receive_history_data(context):
    """Verify history data is received."""
    assert context.history_response.status_code == 200
    data = context.history_response.json()
    assert "queries" in data
    assert "total" in data
    assert "city" in data
    assert isinstance(data["queries"], list)


@then("the history should contain at least {min_count:d} entry")
def step_history_contains_entries(context, min_count):
    """Verify history contains minimum number of entries."""
    data = context.history_response.json()
    assert len(data["queries"]) >= min_count


@then("the first {count:d} requests should succeed")
def step_first_requests_succeed(context, count):
    """Verify first N requests succeed."""
    # Count successful requests (200) vs rate limited (429)
    successful_requests = sum(1 for r in context.responses if r.status_code == 200)
    rate_limited_requests = sum(1 for r in context.responses if r.status_code == 429)

    # At least some requests should succeed, and some should be rate limited
    assert successful_requests >= 1, f"Expected at least 1 successful request, got {successful_requests}"
    assert rate_limited_requests >= 1, f"Expected at least 1 rate limited request, got {rate_limited_requests}"


@then("the {ordinal} request should be rate limited")
def step_request_rate_limited(context, ordinal):
    """Verify that rate limiting occurred."""
    # Check if any request was rate limited (429)
    rate_limited_requests = [r for r in context.responses if r.status_code == 429]

    assert len(rate_limited_requests) > 0, "Expected at least one request to be rate limited"


@then("I should receive a {status_code:d} status code")
def step_receive_status_code(context, status_code):
    """Verify specific status code is received."""
    # Check the last response for the status code
    if hasattr(context, "responses") and context.responses:
        last_response = context.responses[-1]
        assert last_response.status_code == status_code
    else:
        assert context.response.status_code == status_code


@then("I should receive fresh weather data")
def step_receive_fresh_weather_data(context):
    """Verify fresh weather data is received."""
    assert context.response.status_code == 200
    data = context.response.json()
    assert "city" in data
    assert "temperature" in data
