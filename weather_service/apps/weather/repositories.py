"""
Weather app repositories - Data access layer.
"""
import json
from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Any

from django.core.cache import cache
from django.utils import timezone
from loguru import logger

from .models import WeatherCache, WeatherQuery


class WeatherQueryRepositoryInterface(ABC):
    """Interface for weather query repository."""

    @abstractmethod
    def save_query(self, city: str, ip_address: str, weather_data: dict[str, Any]) -> WeatherQuery:
        pass

    @abstractmethod
    def get_history(self, city: str, ip_address: str, limit: int = 10) -> list[WeatherQuery]:
        pass

    @abstractmethod
    def cleanup_old_queries(self, city: str, ip_address: str, limit: int = 10) -> None:
        pass


class WeatherCacheRepositoryInterface(ABC):
    """Interface for weather cache repository."""

    @abstractmethod
    def get_cached_weather(self, city: str) -> dict[str, Any] | None:
        pass

    @abstractmethod
    def cache_weather(self, city: str, weather_data: dict[str, Any], ttl_seconds: int = 600) -> None:
        pass

    @abstractmethod
    def invalidate_cache(self, city: str) -> None:
        pass


class DjangoWeatherQueryRepository(WeatherQueryRepositoryInterface):
    """Django ORM implementation of weather query repository."""

    def save_query(self, city: str, ip_address: str, weather_data: dict[str, Any]) -> WeatherQuery:
        """Save a weather query to the database."""
        try:
            query = WeatherQuery.objects.create(
                city=city,
                ip_address=ip_address,
                temperature=weather_data.get("temperature", 0),
                description=weather_data.get("description", ""),
                humidity=weather_data.get("humidity"),
                pressure=weather_data.get("pressure"),
                wind_speed=weather_data.get("wind_speed"),
                country=weather_data.get("country", ""),
            )
            logger.info(f"Saved weather query for {city} from IP {ip_address}")
            return query
        except Exception as e:
            logger.error(f"Error saving weather query: {e}")
            raise

    def get_history(self, city: str, ip_address: str, limit: int = 10) -> list[WeatherQuery]:
        """Get weather query history for a city and IP."""
        try:
            return list(WeatherQuery.objects.filter(city=city, ip_address=ip_address).order_by("-created_at")[:limit])
        except Exception as e:
            logger.error(f"Error getting weather history: {e}")
            return []

    def cleanup_old_queries(self, city: str, ip_address: str, limit: int = 10) -> None:
        """Clean up old queries, keeping only the last 'limit' entries."""
        try:
            WeatherQuery.cleanup_old_queries(city, ip_address, limit)
            logger.info(f"Cleaned up old queries for {city} from IP {ip_address}")
        except Exception as e:
            logger.error(f"Error cleaning up old queries: {e}")


class RedisWeatherCacheRepository(WeatherCacheRepositoryInterface):
    """Redis implementation of weather cache repository."""

    def __init__(self):
        self.cache_prefix = "weather_cache"

    def _get_cache_key(self, city: str) -> str:
        """Generate cache key for a city."""
        return f"{self.cache_prefix}:{city.lower()}"

    def get_cached_weather(self, city: str) -> dict[str, Any] | None:
        """Get cached weather data for a city."""
        try:
            cache_key = self._get_cache_key(city)
            cached_data = cache.get(cache_key)

            if cached_data:
                logger.info(f"Cache hit for city: {city}")
                return json.loads(cached_data) if isinstance(cached_data, str) else cached_data

            logger.info(f"Cache miss for city: {city}")
            return None
        except Exception as e:
            logger.error(f"Error getting cached weather: {e}")
            return None

    def cache_weather(self, city: str, weather_data: dict[str, Any], ttl_seconds: int = 600) -> None:
        """Cache weather data for a city."""
        try:
            cache_key = self._get_cache_key(city)
            weather_data["cached_at"] = timezone.now().isoformat()

            cache.set(cache_key, json.dumps(weather_data, default=str), ttl_seconds)
            logger.info(f"Cached weather data for {city} with TTL {ttl_seconds}s")
        except Exception as e:
            logger.error(f"Error caching weather data: {e}")

    def invalidate_cache(self, city: str) -> None:
        """Invalidate cached weather data for a city."""
        try:
            cache_key = self._get_cache_key(city)
            cache.delete(cache_key)
            logger.info(f"Invalidated cache for city: {city}")
        except Exception as e:
            logger.error(f"Error invalidating cache: {e}")


class DatabaseWeatherCacheRepository(WeatherCacheRepositoryInterface):
    """Database fallback implementation of weather cache repository."""

    def get_cached_weather(self, city: str) -> dict[str, Any] | None:
        """Get cached weather data from database."""
        try:
            cache_entry = WeatherCache.objects.filter(city=city.lower()).first()

            if cache_entry and not cache_entry.is_expired:
                logger.info(f"Database cache hit for city: {city}")
                return cache_entry.data

            # Clean up expired entry
            if cache_entry and cache_entry.is_expired:
                cache_entry.delete()

            logger.info(f"Database cache miss for city: {city}")
            return None
        except Exception as e:
            logger.error(f"Error getting cached weather from database: {e}")
            return None

    def cache_weather(self, city: str, weather_data: dict[str, Any], ttl_seconds: int = 600) -> None:
        """Cache weather data in database."""
        try:
            expires_at = timezone.now() + timedelta(seconds=ttl_seconds)
            weather_data["cached_at"] = timezone.now().isoformat()

            WeatherCache.objects.update_or_create(
                city=city.lower(),
                defaults={"data": weather_data, "expires_at": expires_at, "created_at": timezone.now()},
            )
            logger.info(f"Cached weather data in database for {city}")
        except Exception as e:
            logger.error(f"Error caching weather data in database: {e}")

    def invalidate_cache(self, city: str) -> None:
        """Invalidate cached weather data in database."""
        try:
            WeatherCache.objects.filter(city=city.lower()).delete()
            logger.info(f"Invalidated database cache for city: {city}")
        except Exception as e:
            logger.error(f"Error invalidating database cache: {e}")
