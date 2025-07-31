"""
Weather app models.
"""
from django.db import models
from django.utils import timezone


class WeatherQuery(models.Model):
    """
    Model to store weather query history.
    Keeps track of the last 10 queries per city/IP combination.
    """

    city = models.CharField(max_length=100, db_index=True)
    ip_address = models.GenericIPAddressField(db_index=True)
    temperature = models.FloatField()
    description = models.CharField(max_length=200)
    humidity = models.IntegerField(null=True, blank=True)
    pressure = models.FloatField(null=True, blank=True)
    wind_speed = models.FloatField(null=True, blank=True)
    country = models.CharField(max_length=2, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["city", "ip_address", "-created_at"]),
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        return f"{self.city} - {self.temperature}°C ({self.created_at})"

    @classmethod
    def cleanup_old_queries(cls, city, ip_address, limit=10):
        """
        Keep only the last 'limit' queries for a city/IP combination.
        """
        queries = cls.objects.filter(city=city, ip_address=ip_address).order_by("-created_at")

        if queries.count() > limit:
            old_queries = queries[limit:]
            cls.objects.filter(id__in=[q.id for q in old_queries]).delete()


class WeatherCache(models.Model):
    """
    Model to store cached weather data.
    Alternative to Redis for persistent caching.
    """

    city = models.CharField(max_length=100, unique=True, db_index=True)
    data = models.JSONField()
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(db_index=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Cache for {self.city}"

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    @classmethod
    def cleanup_expired(cls):
        """Remove expired cache entries."""
        cls.objects.filter(expires_at__lt=timezone.now()).delete()
