"""
Test settings for Weather Service project.
"""
from .base import *

# Test database - SQLite in memory for faster tests
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        "TEST": {
            "NAME": ":memory:",
        },
    }
}


# Disable migrations for faster tests
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


MIGRATION_MODULES = DisableMigrations()

# Cache for tests
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

TESTING = True

# Logging for tests
# Disable logging during tests for cleaner output
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "null": {
            "class": "logging.NullHandler",
        },
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "weather_service": {
            "handlers": ["null"],
            "level": "CRITICAL",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["null"],
            "level": "CRITICAL",
            "propagate": False,
        },
    },
    "root": {
        "handlers": ["null"],
        "level": "CRITICAL",
    },
}
