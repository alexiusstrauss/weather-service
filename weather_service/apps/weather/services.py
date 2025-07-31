"""
Weather app services - External integrations layer.
"""
from abc import ABC, abstractmethod
from typing import Any

import prometheus_client
import requests
from django.conf import settings
from loguru import logger

# Prometheus metrics
weather_api_requests = prometheus_client.Counter(
    "weather_service_external_api_requests_total", "Total number of external API requests", ["provider", "status"]
)

weather_api_duration = prometheus_client.Histogram(
    "weather_service_external_api_duration_seconds", "Duration of external API requests", ["provider"]
)


class WeatherServiceInterface(ABC):
    """Interface for weather service providers."""

    @abstractmethod
    def get_weather(self, city: str) -> dict[str, Any]:
        pass


class OpenWeatherMapService(WeatherServiceInterface):
    """OpenWeatherMap API service implementation."""

    def __init__(self):
        self.api_key = settings.OPENWEATHER_API_KEY
        self.base_url = settings.OPENWEATHER_BASE_URL

        if not self.api_key:
            logger.warning("OpenWeatherMap API key not configured")

    def get_weather(self, city: str) -> dict[str, Any]:
        """
        Get weather data from OpenWeatherMap API.

        Args:
            city: City name to get weather for

        Returns:
            Dictionary with weather data

        Raises:
            WeatherServiceException: If API request fails
        """
        if not self.api_key:
            raise WeatherServiceException("OpenWeatherMap API key not configured")

        url = f"{self.base_url}/weather"
        params = {"q": city, "appid": self.api_key, "units": "metric", "lang": "pt_br"}

        with weather_api_duration.labels(provider="openweathermap").time():
            try:
                logger.info(f"Fetching weather data for {city} from OpenWeatherMap")
                response = requests.get(url, params=params, timeout=10)

                if response.status_code == 200:
                    weather_api_requests.labels(provider="openweathermap", status="success").inc()
                    data = response.json()
                    return self._parse_weather_data(data)

                elif response.status_code == 404:
                    weather_api_requests.labels(provider="openweathermap", status="not_found").inc()
                    raise WeatherServiceException(f"Cidade '{city}' não encontrada")

                elif response.status_code == 401:
                    weather_api_requests.labels(provider="openweathermap", status="unauthorized").inc()
                    raise WeatherServiceException("Chave da API inválida")

                else:
                    weather_api_requests.labels(provider="openweathermap", status="error").inc()
                    logger.error(f"OpenWeatherMap API error: {response.status_code} - {response.text}")
                    raise WeatherServiceException(f"Erro na API: {response.status_code}")

            except requests.RequestException as e:
                weather_api_requests.labels(provider="openweathermap", status="error").inc()
                logger.error(f"Request error: {e}")
                raise WeatherServiceException(f"Erro de conexão: {str(e)}")

    def _parse_weather_data(self, data: dict[str, Any]) -> dict[str, Any]:
        """Parse OpenWeatherMap API response into standardized format."""
        try:
            return {
                "city": data["name"],
                "country": data["sys"]["country"],
                "temperature": round(data["main"]["temp"], 1),
                "description": data["weather"][0]["description"].title(),
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],
                "wind_speed": data.get("wind", {}).get("speed", 0),
                "provider": "openweathermap",
                "raw_data": data,
            }
        except KeyError as e:
            logger.error(f"Error parsing weather data: {e}")
            raise WeatherServiceException(f"Erro ao processar dados da API: {str(e)}")


class MockWeatherService(WeatherServiceInterface):
    """Mock weather service for testing and development."""

    def get_weather(self, city: str) -> dict[str, Any]:
        """Return mock weather data."""
        logger.info(f"Returning mock weather data for {city}")

        if city.lower() in ["error", "fail"]:
            raise WeatherServiceException("Mock error for testing")

        if city.lower() == "notfound":
            raise WeatherServiceException(f"Cidade '{city}' não encontrada")

        return {
            "city": city.title(),
            "country": "BR",
            "temperature": 25.0,
            "description": "Ensolarado",
            "humidity": 60,
            "pressure": 1013.25,
            "wind_speed": 5.5,
            "provider": "mock",
            "raw_data": {"mock": True},
        }


class WeatherServiceException(Exception):
    """Exception raised by weather services."""

    pass


class WeatherServiceFactory:
    """Factory for creating weather service instances."""

    @staticmethod
    def create_service(provider: str = "openweathermap") -> WeatherServiceInterface:
        """
        Create a weather service instance.

        Args:
            provider: Service provider name

        Returns:
            WeatherServiceInterface instance
        """
        if provider == "openweathermap":
            return OpenWeatherMapService()
        elif provider == "mock":
            return MockWeatherService()
        else:
            raise ValueError(f"Unknown weather service provider: {provider}")
