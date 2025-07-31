"""
Weather app serializers.
"""
from rest_framework import serializers

from .models import WeatherQuery


class WeatherQuerySerializer(serializers.ModelSerializer):
    """Serializer for weather query history."""

    class Meta:
        model = WeatherQuery
        fields = [
            "id",
            "city",
            "temperature",
            "description",
            "humidity",
            "pressure",
            "wind_speed",
            "country",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class WeatherResponseSerializer(serializers.Serializer):
    """Serializer for weather API responses."""

    city = serializers.CharField(max_length=100)
    country = serializers.CharField(max_length=2, required=False)
    temperature = serializers.FloatField()
    description = serializers.CharField(max_length=200)
    humidity = serializers.IntegerField(required=False)
    pressure = serializers.FloatField(required=False)
    wind_speed = serializers.FloatField(required=False)
    cached = serializers.BooleanField(default=False)
    timestamp = serializers.DateTimeField(read_only=True)


class WeatherRequestSerializer(serializers.Serializer):
    """Serializer for weather request parameters."""

    city = serializers.CharField(max_length=100, help_text="Nome da cidade para consultar o clima")

    def validate_city(self, value):
        """Validate city name."""
        if not value or not value.strip():
            raise serializers.ValidationError("Nome da cidade é obrigatório")

        # Remove extra spaces and capitalize
        return value.strip().title()


class WeatherHistorySerializer(serializers.Serializer):
    """Serializer for weather history responses."""

    queries = WeatherQuerySerializer(many=True)
    total = serializers.IntegerField()
    city = serializers.CharField(max_length=100)
