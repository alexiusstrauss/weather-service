"""
Celery configuration for weather_service project.
"""
import os

from celery import Celery

ONE_MINUTE = 60.0
ONE_HOUR = 3600.0
THIRTY_MINUTES = 1800.0
FIVE_MINUTES = 300.0

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "weather_service.settings.development")

app = Celery("weather_service")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "cleanup-weather-history-minutely": {
        "task": "weather_service.apps.weather.tasks.cleanup_weather_history_minutely",
        "schedule": ONE_MINUTE,
        "options": {"queue": "default"},
    },
    "cleanup-old-weather-queries": {
        "task": "weather_service.apps.weather.tasks.cleanup_old_weather_queries",
        "schedule": ONE_HOUR,
        "options": {"queue": "default"},
    },
    "cleanup-expired-cache": {
        "task": "weather_service.apps.weather.tasks.cleanup_expired_cache_entries",
        "schedule": THIRTY_MINUTES,
        "options": {"queue": "default"},
    },
    "generate-weather-metrics": {
        "task": "weather_service.apps.weather.tasks.generate_weather_metrics",
        "schedule": FIVE_MINUTES,
        "options": {"queue": "default"},
    },
}

app.conf.timezone = "UTC"


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
