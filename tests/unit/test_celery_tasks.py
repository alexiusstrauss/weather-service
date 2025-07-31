"""
Unit tests for Celery tasks.
"""
from unittest.mock import MagicMock, patch

import pytest
from django.test import TestCase
from django.utils import timezone

from weather_service.apps.weather.models import WeatherQuery
from weather_service.apps.weather.tasks import cleanup_weather_history_minutely


class TestCeleryTasks(TestCase):
    """Test Celery tasks."""

    def setUp(self):
        """Set up test data."""
        # Create test weather queries for different cities
        self.test_queries = []

        # Create 15 queries for London (should keep only 10)
        for i in range(15):
            query = WeatherQuery.objects.create(
                city="London",
                ip_address="127.0.0.1",
                temperature=20.0 + i,
                description=f"Test weather {i}",
                created_at=timezone.now(),
            )
            self.test_queries.append(query)

        # Create 5 queries for Paris (should keep all 5)
        for i in range(5):
            query = WeatherQuery.objects.create(
                city="Paris",
                ip_address="127.0.0.1",
                temperature=15.0 + i,
                description=f"Paris weather {i}",
                created_at=timezone.now(),
            )
            self.test_queries.append(query)

    def test_cleanup_weather_history_minutely_success(self):
        """Test successful cleanup of weather history."""
        # Verify initial state
        london_count = WeatherQuery.objects.filter(city="London").count()
        paris_count = WeatherQuery.objects.filter(city="Paris").count()

        assert london_count == 15
        assert paris_count == 5

        # Run the cleanup task
        result = cleanup_weather_history_minutely()

        # Verify results
        london_count_after = WeatherQuery.objects.filter(city="London").count()
        paris_count_after = WeatherQuery.objects.filter(city="Paris").count()

        # London should have only 10 records (5 deleted)
        assert london_count_after == 10
        # Paris should still have 5 records (none deleted)
        assert paris_count_after == 5

        # Check return message
        assert "Deleted 5 old queries" in result

    def test_cleanup_weather_history_minutely_no_data(self):
        """Test cleanup when no data exists."""
        # Clear all data
        WeatherQuery.objects.all().delete()

        # Run the cleanup task
        result = cleanup_weather_history_minutely()

        # Should complete successfully with no deletions
        assert "Deleted 0 old queries" in result

    def test_cleanup_weather_history_minutely_keeps_recent_records(self):
        """Test that cleanup keeps the most recent records."""
        # Get the IDs of the most recent 10 London records
        recent_london_ids = list(
            WeatherQuery.objects.filter(city="London").order_by("-created_at")[:10].values_list("id", flat=True)
        )

        # Run cleanup
        cleanup_weather_history_minutely()

        # Verify that all remaining London records are from the recent list
        remaining_london_ids = list(WeatherQuery.objects.filter(city="London").values_list("id", flat=True))

        assert len(remaining_london_ids) == 10
        assert set(remaining_london_ids) == set(recent_london_ids)

    @patch("weather_service.apps.weather.tasks.logger")
    def test_cleanup_weather_history_minutely_logs_activity(self, mock_logger):
        """Test that the task logs its activity."""
        # Run the task
        cleanup_weather_history_minutely()

        # Verify logging calls
        mock_logger.info.assert_any_call("Starting minutely cleanup of weather query history")
        mock_logger.info.assert_any_call("Deleted 5 old queries for city: London")
        mock_logger.info.assert_any_call("Minutely cleanup completed. Total deleted: 5 queries")

    @patch("weather_service.apps.weather.tasks.WeatherQuery.objects")
    def test_cleanup_weather_history_minutely_handles_database_error(self, mock_objects):
        """Test that the task handles database errors gracefully."""
        # Mock database error
        mock_objects.values_list.side_effect = Exception("Database connection error")

        # The task should raise the exception
        with pytest.raises(Exception) as exc_info:
            cleanup_weather_history_minutely()

        assert "Database connection error" in str(exc_info.value)

    def test_cleanup_weather_history_minutely_multiple_cities(self):
        """Test cleanup with multiple cities having different record counts."""
        # Add more cities with different record counts
        cities_data = [
            ("Tokyo", 12),  # Should delete 2
            ("Berlin", 8),  # Should delete 0
            ("Madrid", 20),  # Should delete 10
        ]

        for city, count in cities_data:
            for i in range(count):
                WeatherQuery.objects.create(
                    city=city,
                    ip_address="127.0.0.1",
                    temperature=20.0 + i,
                    description=f"{city} weather {i}",
                    created_at=timezone.now(),
                )

        # Run cleanup
        result = cleanup_weather_history_minutely()

        # Verify results
        for city, original_count in cities_data:
            remaining_count = WeatherQuery.objects.filter(city=city).count()
            expected_count = min(original_count, 10)
            assert (
                remaining_count == expected_count
            ), f"City {city} should have {expected_count} records, got {remaining_count}"

        # Total deletions: London(5) + Tokyo(2) + Madrid(10) = 17
        assert "Deleted 17 old queries" in result


class TestCeleryTaskIntegration(TestCase):
    """Integration tests for Celery tasks."""

    @patch("weather_service.apps.weather.tasks.cleanup_weather_history_minutely.delay")
    def test_task_can_be_called_asynchronously(self, mock_delay):
        """Test that the task can be called asynchronously."""
        # Mock the async call
        mock_result = MagicMock()
        mock_result.id = "test-task-id-123"
        mock_delay.return_value = mock_result

        # Call the task asynchronously
        result = cleanup_weather_history_minutely.delay()

        # Verify the call
        mock_delay.assert_called_once()
        assert result.id == "test-task-id-123"
