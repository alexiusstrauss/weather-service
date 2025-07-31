"""
Weather app use cases - Business logic layer.
"""
from abc import ABC, abstractmethod
from typing import Any

import prometheus_client
from django.utils import timezone
from loguru import logger

from .repositories import (
    DjangoWeatherQueryRepository,
    RedisWeatherCacheRepository,
    WeatherCacheRepositoryInterface,
    WeatherQueryRepositoryInterface,
)
from .services import WeatherServiceException, WeatherServiceFactory, WeatherServiceInterface

ONE_MINUTE = 60.0

# Prometheus metrics
weather_requests = prometheus_client.Counter(
    "weather_service_requests_total", "Total number of weather requests", ["city", "cached"]
)

weather_cache_hits = prometheus_client.Counter("weather_service_cache_hits_total", "Total number of cache hits")

weather_cache_misses = prometheus_client.Counter("weather_service_cache_misses_total", "Total number of cache misses")

weather_request_duration = prometheus_client.Histogram(
    "weather_service_request_duration_seconds", "Duration of weather requests", ["cached"]
)


class GetWeatherUseCaseInterface(ABC):
    """Interface for get weather use case."""

    @abstractmethod
    def execute(self, city: str, ip_address: str) -> dict[str, Any]:
        """
        Execute the get weather use case.

        Args:
            city: City name to get weather for
            ip_address: Client IP address for rate limiting and tracking

        Returns:
            Dictionary containing weather data and metadata
        """
        ...


class GetWeatherHistoryUseCaseInterface(ABC):
    """Interface for get weather history use case."""

    @abstractmethod
    def execute(self, city: str, ip_address: str, limit: int = 10) -> dict[str, Any]:
        """
        Execute the get weather history use case.

        Args:
            city: City name to get history for
            ip_address: Client IP address
            limit: Maximum number of history entries to return

        Returns:
            Dictionary containing history data
        """
        ...


class GetWeatherUseCase(GetWeatherUseCaseInterface):
    """
    Use case for getting weather data.
    Implements caching and history tracking.
    """

    def __init__(
        self,
        weather_service: WeatherServiceInterface | None = None,
        cache_repository: WeatherCacheRepositoryInterface | None = None,
        query_repository: WeatherQueryRepositoryInterface | None = None,
    ):
        if weather_service is None:
            from django.conf import settings

            api_key = getattr(settings, "OPENWEATHER_API_KEY", "")
            if not api_key or api_key == "your_openweathermap_api_key_here":
                self.weather_service = WeatherServiceFactory.create_service("mock")
            else:
                self.weather_service = WeatherServiceFactory.create_service()
        else:
            self.weather_service = weather_service
        self.cache_repository = cache_repository or RedisWeatherCacheRepository()
        self.query_repository = query_repository or DjangoWeatherQueryRepository()

    def execute(self, city: str, ip_address: str) -> dict[str, Any]:
        """
        Execute the get weather use case.

        Args:
            city: City name to get weather for
            ip_address: Client IP address for rate limiting and history

        Returns:
            Dictionary with weather data and metadata

        Raises:
            WeatherServiceException: If weather data cannot be retrieved
        """
        city = city.strip().title()
        logger.info(f"Getting weather for {city} from IP {ip_address}")

        # Try to get from cache first
        with weather_request_duration.labels(cached="check").time():
            cached_data = self.cache_repository.get_cached_weather(city)

        if cached_data:
            weather_cache_hits.inc()
            weather_requests.labels(city=city, cached="true").inc()

            # Add metadata
            cached_data["cached"] = True
            cached_data["timestamp"] = timezone.now()

            logger.info(f"Returning cached weather data for {city}")
            return cached_data

        # Cache miss - get from external service
        weather_cache_misses.inc()

        with weather_request_duration.labels(cached="false").time():
            try:
                weather_data = self.weather_service.get_weather(city)
                weather_requests.labels(city=city, cached="false").inc()

                # Cache the data
                self.cache_repository.cache_weather(city, weather_data, ttl_seconds=ONE_MINUTE)

                # Save to history (async task would be better)
                self._save_to_history(city, ip_address, weather_data)

                # Add metadata
                weather_data["cached"] = False
                weather_data["timestamp"] = timezone.now()

                logger.info(f"Retrieved and cached weather data for {city}")
                return weather_data

            except WeatherServiceException as e:
                logger.error(f"Weather service error for {city}: {e}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error getting weather for {city}: {e}")
                raise WeatherServiceException(f"Erro interno do serviço: {str(e)}")

    def _save_to_history(self, city: str, ip_address: str, weather_data: dict[str, Any]) -> None:
        """Save weather query to history."""
        try:
            self.query_repository.save_query(city, ip_address, weather_data)
            self.query_repository.cleanup_old_queries(city, ip_address, limit=10)
        except Exception as e:
            # Don't fail the main request if history saving fails
            logger.error(f"Error saving weather query to history: {e}")


class GetWeatherHistoryUseCase(GetWeatherHistoryUseCaseInterface):
    """
    Use case for getting weather query history.
    """

    def __init__(self, query_repository: WeatherQueryRepositoryInterface | None = None):
        self.query_repository = query_repository or DjangoWeatherQueryRepository()

    def execute(self, city: str, ip_address: str, limit: int = 10) -> dict[str, Any]:
        """
        Execute the get weather history use case.

        Args:
            city: City name to get history for
            ip_address: Client IP address
            limit: Maximum number of history entries to return

        Returns:
            Dictionary with history data
        """
        city = city.strip().title()
        logger.info(f"Getting weather history for {city} from IP {ip_address}")

        try:
            queries = self.query_repository.get_history(city, ip_address, limit)

            return {"city": city, "queries": queries, "total": len(queries), "limit": limit}

        except Exception as e:
            logger.error(f"Error getting weather history: {e}")
            raise WeatherServiceException(f"Erro ao buscar histórico: {str(e)}")


class InvalidateCacheUseCase:
    """Use case for invalidating weather cache."""

    def __init__(self, cache_repository: WeatherCacheRepositoryInterface | None = None):
        self.cache_repository = cache_repository or RedisWeatherCacheRepository()

    def execute(self, city: str) -> None:
        """
        Invalidate cache for a city.

        Args:
            city: City name to invalidate cache for
        """
        city = city.strip().title()
        logger.info(f"Invalidating cache for {city}")

        try:
            self.cache_repository.invalidate_cache(city)
            logger.info(f"Cache invalidated for {city}")
        except Exception as e:
            logger.error(f"Error invalidating cache for {city}: {e}")
            raise WeatherServiceException(f"Erro ao invalidar cache: {str(e)}")


class CleanupHistoryUseCase:
    """Use case for cleaning up old weather queries."""

    def __init__(self, query_repository: WeatherQueryRepositoryInterface | None = None):
        self.query_repository = query_repository or DjangoWeatherQueryRepository()

    def execute(self, city: str, ip_address: str, limit: int = 10) -> None:
        """
        Clean up old weather queries.

        Args:
            city: City name
            ip_address: Client IP address
            limit: Number of queries to keep
        """
        logger.info(f"Cleaning up history for {city} from IP {ip_address}")

        try:
            self.query_repository.cleanup_old_queries(city, ip_address, limit)
            logger.info(f"History cleaned up for {city}")
        except Exception as e:
            logger.error(f"Error cleaning up history: {e}")
            raise WeatherServiceException(f"Erro ao limpar histórico: {str(e)}")
