"""
Development settings for Weather Service project.
"""
from .base import *

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0", "api"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME", default="weather_service"),
        "USER": config("DB_USER", default="weather_user"),
        "PASSWORD": config("DB_PASSWORD", default="weather_pass"),
        "HOST": config("DB_HOST", default="localhost"),
        "PORT": config("DB_PORT", default="5432"),
    }
}

INSTALLED_APPS += [
    "django_extensions",
]
MIDDLEWARE = [
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
] + MIDDLEWARE[1:]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
        "KEY_PREFIX": "weather_service_dev",
        "TIMEOUT": 600,
    }
}

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

LOGGING["handlers"]["console"]["level"] = "DEBUG"
LOGGING["loggers"]["weather_service"]["level"] = "DEBUG"
