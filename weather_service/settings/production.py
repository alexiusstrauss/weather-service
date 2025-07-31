"""
Production settings for Weather Service project.
"""
from .base import *

DEBUG = False

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True


import dj_database_url

DATABASES["default"] = dj_database_url.parse(
    config("DATABASE_URL", default="postgresql://weather_user:weather_pass@localhost:5432/weather_service")
)

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config("EMAIL_HOST", default="localhost")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

LOGGING["handlers"]["file"]["filename"] = "/var/log/weather_service/django.log"
