"""
Unit tests for weather services.
"""
from unittest.mock import Mock, patch

import pytest
import requests

from weather_service.apps.weather.services import (
    MockWeatherService,
    OpenWeatherMapService,
    WeatherServiceException,
    WeatherServiceFactory,
)


class TestOpenWeatherMapService:
    """Test cases for OpenWeatherMapService."""

    def test_init_without_api_key(self, settings):
        """Test initialization without API key."""
        settings.OPENWEATHER_API_KEY = ""
        service = OpenWeatherMapService()
        assert service.api_key == ""

    def test_init_with_api_key(self, settings):
        """Test initialization with API key."""
        settings.OPENWEATHER_API_KEY = "test-key"
        service = OpenWeatherMapService()
        assert service.api_key == "test-key"

    def test_get_weather_without_api_key(self, settings):
        """Test get_weather without API key raises exception."""
        settings.OPENWEATHER_API_KEY = ""
        service = OpenWeatherMapService()

        with pytest.raises(WeatherServiceException, match="API key not configured"):
            service.get_weather("São Paulo")

    @patch("weather_service.apps.weather.services.requests.get")
    def test_get_weather_success(self, mock_get, settings, openweather_api_response):
        """Test successful weather data retrieval."""
        settings.OPENWEATHER_API_KEY = "test-key"

        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = openweather_api_response
        mock_get.return_value = mock_response

        service = OpenWeatherMapService()
        result = service.get_weather("São Paulo")

        assert result["city"] == "São Paulo"
        assert result["country"] == "BR"
        assert result["temperature"] == 25.0
        assert result["provider"] == "openweathermap"

        # Verify API call
        mock_get.assert_called_once()
        _, kwargs = mock_get.call_args
        assert kwargs.get("params", {}).get("q") == "São Paulo"

    @patch("weather_service.apps.weather.services.requests.get")
    def test_get_weather_city_not_found(self, mock_get, settings):
        """Test weather data retrieval for non-existent city."""
        settings.OPENWEATHER_API_KEY = "test-key"

        # Mock 404 response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        service = OpenWeatherMapService()

        with pytest.raises(WeatherServiceException, match="não encontrada"):
            service.get_weather("NonExistentCity")

    @patch("weather_service.apps.weather.services.requests.get")
    def test_get_weather_unauthorized(self, mock_get, settings):
        """Test weather data retrieval with invalid API key."""
        settings.OPENWEATHER_API_KEY = "invalid-key"

        # Mock 401 response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        service = OpenWeatherMapService()

        with pytest.raises(WeatherServiceException, match="Chave da API inválida"):
            service.get_weather("São Paulo")

    @patch("weather_service.apps.weather.services.requests.get")
    def test_get_weather_api_error(self, mock_get, settings):
        """Test weather data retrieval with API error."""
        settings.OPENWEATHER_API_KEY = "test-key"

        # Mock 500 response
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        service = OpenWeatherMapService()

        with pytest.raises(WeatherServiceException, match="Erro na API"):
            service.get_weather("São Paulo")

    @patch("weather_service.apps.weather.services.requests.get")
    def test_get_weather_connection_error(self, mock_get, settings):
        """Test weather data retrieval with connection error."""
        settings.OPENWEATHER_API_KEY = "test-key"

        # Mock connection error
        mock_get.side_effect = requests.ConnectionError("Connection failed")

        service = OpenWeatherMapService()

        with pytest.raises(WeatherServiceException, match="Erro de conexão"):
            service.get_weather("São Paulo")

    def test_parse_weather_data_success(self, settings, openweather_api_response):
        """Test successful parsing of weather data."""
        settings.OPENWEATHER_API_KEY = "test-key"
        service = OpenWeatherMapService()

        result = service._parse_weather_data(openweather_api_response)

        assert result["city"] == "São Paulo"
        assert result["country"] == "BR"
        assert result["temperature"] == 25.0
        assert result["description"] == "Ensolarado"
        assert result["humidity"] == 60
        assert result["pressure"] == 1013.25
        assert result["wind_speed"] == 5.5
        assert result["provider"] == "openweathermap"

    def test_parse_weather_data_missing_field(self, settings):
        """Test parsing weather data with missing fields."""
        settings.OPENWEATHER_API_KEY = "test-key"
        service = OpenWeatherMapService()

        incomplete_data = {"name": "São Paulo"}  # Missing required fields

        with pytest.raises(WeatherServiceException, match="Erro ao processar dados"):
            service._parse_weather_data(incomplete_data)


class TestMockWeatherService:
    """Test cases for MockWeatherService."""

    def test_get_weather_success(self):
        """Test successful mock weather data retrieval."""
        service = MockWeatherService()
        result = service.get_weather("São Paulo")

        assert result["city"] == "São Paulo"
        assert result["country"] == "BR"
        assert result["temperature"] == 25.0
        assert result["provider"] == "mock"

    def test_get_weather_error_case(self):
        """Test mock error case."""
        service = MockWeatherService()

        with pytest.raises(WeatherServiceException, match="Mock error"):
            service.get_weather("error")

    def test_get_weather_not_found_case(self):
        """Test mock not found case."""
        service = MockWeatherService()

        with pytest.raises(WeatherServiceException, match="não encontrada"):
            service.get_weather("notfound")


class TestWeatherServiceFactory:
    """Test cases for WeatherServiceFactory."""

    def test_create_openweathermap_service(self):
        """Test creating OpenWeatherMap service."""
        service = WeatherServiceFactory.create_service("openweathermap")
        assert isinstance(service, OpenWeatherMapService)

    def test_create_mock_service(self):
        """Test creating mock service."""
        service = WeatherServiceFactory.create_service("mock")
        assert isinstance(service, MockWeatherService)

    def test_create_unknown_service(self):
        """Test creating unknown service raises error."""
        with pytest.raises(ValueError, match="Unknown weather service provider"):
            WeatherServiceFactory.create_service("unknown")

    def test_create_default_service(self):
        """Test creating default service."""
        service = WeatherServiceFactory.create_service()
        assert isinstance(service, OpenWeatherMapService)
