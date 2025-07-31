"""
Behave environment configuration for BDD tests.
"""
import os

import django
from django.test.utils import setup_test_environment, teardown_test_environment
from loguru import logger


def before_all(context):
    """Set up test environment before all tests."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "weather_service.settings.test")
    django.setup()
    setup_test_environment()

    # Disable loguru logging during tests for cleaner output
    logger.disable("")

    # Enable rate limiting specifically for BDD tests
    from django.conf import settings

    settings.BDD_RATE_LIMITING_ENABLED = True

    # Create database tables for tests
    from django.core.management import call_command

    call_command("migrate", "--run-syncdb", verbosity=0)


def after_all(context):
    """Clean up after all tests."""
    teardown_test_environment()


def before_scenario(context, scenario):
    """Set up before each scenario."""
    # Clear any cached data, except for rate limiting scenario
    if "Rate limiting" not in scenario.name:
        from django.core.cache import cache

        cache.clear()


def after_scenario(context, scenario):
    """Clean up after each scenario."""
    # Clean up any test data
    from django.core.management import call_command

    call_command("flush", "--noinput")
