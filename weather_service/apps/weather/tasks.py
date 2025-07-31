"""
Weather app Celery tasks.
"""
from datetime import timedelta

from celery import shared_task
from django.utils import timezone
from loguru import logger

from .models import WeatherCache, WeatherQuery
from .usecases import CleanupHistoryUseCase


@shared_task
def cleanup_weather_history_minutely():
    """
    Periodic task to maintain weather query history.
    Runs every minute and keeps only the last 10 queries per city.
    This ensures the history table doesn't grow indefinitely.
    """
    logger.info("Starting minutely cleanup of weather query history")

    try:
        from django.db import connection

        # Get all unique cities
        unique_cities = WeatherQuery.objects.values_list("city", flat=True).distinct()

        total_deleted = 0
        for city in unique_cities:
            # Keep only the 10 most recent queries per city
            # Using raw SQL for better performance
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM weather_weatherquery
                    WHERE city = %s AND id NOT IN (
                        SELECT id FROM (
                            SELECT id FROM weather_weatherquery
                            WHERE city = %s
                            ORDER BY created_at DESC
                            LIMIT 10
                        ) AS recent_queries
                    )
                """,
                    [city, city],
                )
                deleted_count = cursor.rowcount
                total_deleted += deleted_count

                if deleted_count > 0:
                    logger.info(f"Deleted {deleted_count} old queries for city: {city}")

        logger.info(f"Minutely cleanup completed. Total deleted: {total_deleted} queries")
        return f"Deleted {total_deleted} old queries"

    except Exception as e:
        logger.error(f"Error in cleanup_weather_history_minutely task: {e}")
        raise


@shared_task
def cleanup_old_weather_queries():
    """
    Periodic task to clean up old weather queries.
    Keeps only the last 10 queries per city/IP combination.
    """
    logger.info("Starting cleanup of old weather queries")

    try:
        # Get all unique city/IP combinations
        unique_combinations = WeatherQuery.objects.values("city", "ip_address").distinct()

        cleanup_count = 0
        for combination in unique_combinations:
            city = combination["city"]
            ip_address = combination["ip_address"]

            # Use the use case to clean up
            use_case = CleanupHistoryUseCase()
            use_case.execute(city, ip_address, limit=10)
            cleanup_count += 1

        logger.info(f"Cleaned up weather queries for {cleanup_count} city/IP combinations")
        return f"Cleaned up {cleanup_count} combinations"

    except Exception as e:
        logger.error(f"Error in cleanup_old_weather_queries task: {e}")
        raise


@shared_task
def cleanup_expired_cache_entries():
    """
    Periodic task to clean up expired cache entries from database.
    """
    logger.info("Starting cleanup of expired cache entries")

    try:
        expired_count = WeatherCache.objects.filter(expires_at__lt=timezone.now()).count()

        WeatherCache.cleanup_expired()

        logger.info(f"Cleaned up {expired_count} expired cache entries")
        return f"Cleaned up {expired_count} expired entries"

    except Exception as e:
        logger.error(f"Error in cleanup_expired_cache_entries task: {e}")
        raise


@shared_task
def cleanup_old_weather_data(days_to_keep=30):
    """
    Periodic task to clean up very old weather data.

    Args:
        days_to_keep: Number of days of data to keep (default: 30)
    """
    logger.info(f"Starting cleanup of weather data older than {days_to_keep} days")

    try:
        cutoff_date = timezone.now() - timedelta(days=days_to_keep)

        # Clean up old weather queries
        old_queries_count = WeatherQuery.objects.filter(created_at__lt=cutoff_date).count()

        WeatherQuery.objects.filter(created_at__lt=cutoff_date).delete()

        # Clean up old cache entries
        old_cache_count = WeatherCache.objects.filter(created_at__lt=cutoff_date).count()

        WeatherCache.objects.filter(created_at__lt=cutoff_date).delete()

        logger.info(f"Cleaned up {old_queries_count} old queries and " f"{old_cache_count} old cache entries")

        return f"Cleaned up {old_queries_count} queries and {old_cache_count} cache entries"

    except Exception as e:
        logger.error(f"Error in cleanup_old_weather_data task: {e}")
        raise


@shared_task
def generate_weather_metrics():
    """
    Periodic task to generate weather service metrics.
    """
    logger.info("Generating weather service metrics")

    try:
        from datetime import timedelta

        from django.db.models import Count

        # Get metrics for the last 24 hours
        last_24h = timezone.now() - timedelta(hours=24)

        metrics = {
            "total_queries_24h": WeatherQuery.objects.filter(created_at__gte=last_24h).count(),
            "unique_cities_24h": WeatherQuery.objects.filter(created_at__gte=last_24h)
            .values("city")
            .distinct()
            .count(),
            "unique_ips_24h": WeatherQuery.objects.filter(created_at__gte=last_24h)
            .values("ip_address")
            .distinct()
            .count(),
            "top_cities_24h": list(
                WeatherQuery.objects.filter(created_at__gte=last_24h)
                .values("city")
                .annotate(count=Count("city"))
                .order_by("-count")[:10]
            ),
            "cache_entries": WeatherCache.objects.count(),
            "total_queries": WeatherQuery.objects.count(),
        }

        logger.info(f"Generated metrics: {metrics}")
        return metrics

    except Exception as e:
        logger.error(f"Error in generate_weather_metrics task: {e}")
        raise
