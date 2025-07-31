"""
Pytest configuration and fixtures.
"""
from unittest.mock import Mock

import factory
import pytest
from django.contrib.auth.models import User
from django.test import Client
from rest_framework.test import APIClient

from weather_service.apps.weather.models import WeatherCache, WeatherQuery
from weather_service.apps.weather.services import WeatherServiceInterface


class WeatherQueryFactory(factory.django.DjangoModelFactory):
    """Factory for WeatherQuery model."""

    class Meta:
        model = WeatherQuery

    city = factory.Faker("city")
    ip_address = factory.Faker("ipv4")
    temperature = factory.Faker("pyfloat", min_value=-20, max_value=45, right_digits=1)
    description = factory.Faker("sentence", nb_words=3)
    humidity = factory.Faker("pyint", min_value=0, max_value=100)
    pressure = factory.Faker("pyfloat", min_value=950, max_value=1050, right_digits=2)
    wind_speed = factory.Faker("pyfloat", min_value=0, max_value=30, right_digits=1)
    country = factory.Faker("country_code")


class WeatherCacheFactory(factory.django.DjangoModelFactory):
    """Factory for WeatherCache model."""

    class Meta:
        model = WeatherCache

    city = factory.Faker("city")
    data = factory.LazyAttribute(
        lambda obj: {
            "city": obj.city,
            "temperature": 25.0,
            "description": "Sunny",
            "humidity": 60,
            "pressure": 1013.25,
            "wind_speed": 5.5,
            "country": "BR",
        }
    )


@pytest.fixture
def api_client():
    """API client fixture."""
    return APIClient()


@pytest.fixture
def django_client():
    """Django test client fixture."""
    return Client()


@pytest.fixture
def user():
    """User fixture."""
    return User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")


@pytest.fixture
def weather_query():
    """WeatherQuery fixture."""
    return WeatherQueryFactory()


@pytest.fixture
def weather_cache():
    """WeatherCache fixture."""
    return WeatherCacheFactory()


@pytest.fixture
def mock_weather_service():
    """Mock weather service fixture."""
    mock_service = Mock(spec=WeatherServiceInterface)
    mock_service.get_weather.return_value = {
        "city": "São Paulo",
        "country": "BR",
        "temperature": 25.0,
        "description": "Ensolarado",
        "humidity": 60,
        "pressure": 1013.25,
        "wind_speed": 5.5,
        "provider": "mock",
    }
    return mock_service


@pytest.fixture
def sample_weather_data():
    """Sample weather data fixture."""
    return {
        "city": "São Paulo",
        "country": "BR",
        "temperature": 25.0,
        "description": "Ensolarado",
        "humidity": 60,
        "pressure": 1013.25,
        "wind_speed": 5.5,
        "provider": "openweathermap",
    }


@pytest.fixture
def openweather_api_response():
    """Sample OpenWeatherMap API response."""
    return {
        "name": "São Paulo",
        "sys": {"country": "BR"},
        "main": {"temp": 25.0, "humidity": 60, "pressure": 1013.25},
        "weather": [{"description": "ensolarado"}],
        "wind": {"speed": 5.5},
    }


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """
    Allow database access for all tests.
    """
    pass


@pytest.fixture
def clear_cache():
    """Clear Django cache before test."""
    from django.core.cache import cache

    cache.clear()
    yield
    cache.clear()
